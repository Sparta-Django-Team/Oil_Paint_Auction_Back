# rest_framework
from rest_framework import serializers

# django
from django.utils import timezone

# auctions
from .models import Auction, Comment, AuctionHistory
from .validators import AuctionBidValidator

# users
from users.models import User

# paintings
from paintings.models import Painting
from paintings.serializers import PaintingDetailSerializer


# 경매 생성 serializer
class AuctionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = (
            "start_bid",
            "end_date",
            "now_bid",
        )
        extra_kwargs = {
            "start_bid": {
                "error_messages": {
                    "required": "입찰가를 입력해주세요.",
                    "blank": "입찰가를 입력해주세요.",
                }
            },
            "end_date": {
                "error_messages": {
                    "required": "날짜를 입력해주세요.",
                    "blank": "날짜를 입력해주세요.",
                }
            },
        }

    def validate(self, data):
        start_bid = data.get("start_bid")
        end_date = data.get("end_date")

        # 시작 입찰가는 10000원 이상 가능
        if start_bid < 10000:
            raise serializers.ValidationError(detail={"start_bid": "시작 입찰가는 10000원 이상만 가능합니다."})

        # 종료일은 현재시간 이후만 가능
        if end_date < timezone.now():
            raise serializers.ValidationError(detail={"end_date": "종료일은 현재시간 이후만 가능합니다."})

        return data


# 경매 리스트 serializer
class AuctionListSerializer(serializers.ModelSerializer):
    auction_like_count = serializers.IntegerField()
    painting = PaintingDetailSerializer()


    class Meta:
        model = Auction
        fields = (
            "id",
            "auction_like_count",
            "painting",
            "start_bid",
            "now_bid",
            "start_date",
            "end_date",
            "bidder",
            "seller",
        )



# 경매 상세 serializer
class AuctionDetailSerializer(serializers.ModelSerializer):
    auction_like_count = serializers.SerializerMethodField()
    painting = PaintingDetailSerializer()

    def get_auction_like_count(self, obj):
        return obj.auction_like.count()

    class Meta:
        model = Auction
        fields = (
            "id",
            "auction_like_count",
            "painting",
            "start_bid",
            "now_bid",
            "start_date",
            "end_date",
            "bidder",
            "seller",
            "auction_like",
        )


# 경매 입찰 serializer
class AuctionBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = (
            "id",
            "start_bid",
            "now_bid",
            "bidder",
        )

    def validate(self, data):
        auction = self.context.get("auction")
        request_user = self.context.get("request").user
        user = User.objects.get(id=request_user.id)

        start_bid = auction.start_bid  
        now_bid = auction.now_bid  
        bidder_id = auction.bidder_id
        enter_bid = data["now_bid"] 

        validator = AuctionBidValidator()
        validator.validate_auction_status(auction)
        validator.validate_owner_cannot_bid(request_user, auction)
        validator.validate_not_highest_bidder(request_user, bidder_id)
        validator.validate_sufficient_points(request_user, enter_bid)
        validator.validate_bid_increment(enter_bid)
        validator.validate_enter_bid_against_start_bid(enter_bid, start_bid)
        validator.validate_enter_bid_against_now_bid(enter_bid, now_bid)

        self.process_bid(auction, request_user, user, enter_bid)

        return data

    def update(self, instance, validated_data):
        instance.now_bid = validated_data.get("now_bid", instance.now_bid)
        instance.bidder = validated_data.get("bidder", self.context.get("request").user)  # 현재 user가 bidder로 바뀜
        instance.save()

        return instance

    def process_bid(self, auction, request_user, user, enter_bid):
        self.refund_previous_bid(auction, request_user, user)
        self.create_auction_history(auction, request_user, enter_bid)
        self.deduct_bid_points(user, enter_bid)
    
    def refund_previous_bid(self, auction, request_user, user):
        auction_history = AuctionHistory.objects.filter(auction=auction, bidder=request_user).last()
        if auction_history:  
            before_now_bid = auction_history.now_bid
            user.point += before_now_bid
            user.save()

    def create_auction_history(self, auction, request_user, enter_bid):
        AuctionHistory.objects.create(now_bid=enter_bid, bidder=request_user, auction=auction)

    def deduct_bid_points(self, user, enter_bid):
        user.point -= enter_bid
        user.save()

# 경매 거래내역 serializer
class AuctionHistoySerializer(serializers.ModelSerializer):
    bidder = serializers.SerializerMethodField()
    auction = serializers.SerializerMethodField()
    bidder_profile_image = serializers.SerializerMethodField()

    def get_bidder(self, obj):
        return obj.bidder.nickname

    def get_auction(self, obj):
        return obj.auction.painting.title

    def get_bidder_profile_image(self, obj):
        return obj.bidder.profile_image.url

    class Meta:
        model = AuctionHistory
        fields = (
            "id",
            "bidder",
            "auction",
            "bidder_profile_image",
            "now_bid",
            "created_at",
        )


# 경매 검색 serializer
class AuctionSearchSerializer(serializers.ModelSerializer):
    paintings = AuctionDetailSerializer(many=True)

    class Meta:
        model = Painting
        fields = (
            "id",
            "paintings",
        )


# 경매 댓글 serializer(상세, 리스트)
class AuctionCommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    auction = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.nickname

    def get_profile_image(self, obj):
        return obj.user.profile_image.url

    def get_auction(self, obj):
        return obj.auction.painting.title

    class Meta:
        model = Comment
        fields = (
            "id",
            "user",
            "profile_image",
            "auction",
            "content",
            "created_at",
            "updated_at",
        )


# 경매 댓글 생성 serializer
class AuctionCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("content",)
        extra_kwargs = {
            "content": {
                "error_messages": {
                    "required": "내용을 입력해주세요.",
                    "blank": "내용을 입력해주세요.",
                }
            },
        }
