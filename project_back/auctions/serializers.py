from rest_framework import serializers

from django.utils import timezone

from auctions.models import Auction, Comment, AuctionHistory
from users.models import User
from paintings.models import Painting
from paintings.serializers import PaintingDetailSerializer

#경매 생성 serializer
class AuctionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ('start_bid', 'end_date','now_bid', )
        extra_kwargs = {'start_bid':{
                        'error_messages': {
                        'required':'입찰가를 입력해주세요.',
                        'blank':'입찰가를 입력해주세요.',}},
                        
                        'end_date':{
                        'error_messages': {
                        'required':'날짜를 입력해주세요.',
                        'blank':'날짜를 입력해주세요.',}},
                        }

    def validate(self, data):
        start_bid = data.get('start_bid')
        end_date = data.get('end_date')
        
        #시작 입찰가는 10000원 이상 가능

        if start_bid < 10000 :
            raise serializers.ValidationError(detail={"start_bid": "시작 입찰가는 10000원 이상만 가능합니다."})
        
        #종료일은 현재시간 이후만 가능
        if end_date < timezone.now():
            raise serializers.ValidationError(detail={"end_date": "종료일은 현재시간 이후만 가능합니다."})

        return data

#경매 리스트 serializer
class AuctionListSerializer(serializers.ModelSerializer):
    auction_like_count = serializers.SerializerMethodField()
    painting = PaintingDetailSerializer()
    seller = serializers.SerializerMethodField()
    
    def get_auction_like_count(self, obj):    
        return obj.auction_like.count()
    
    def get_seller(self, obj):
        return obj.seller.nickname

    class Meta:
        model = Auction
        fields = ('id', 'auction_like_count', 'painting', 'start_bid', 'now_bid', 'start_date', 'end_date', 'bidder', 'seller', )

#경매 상세 serializer
class AuctionDetailSerializer(serializers.ModelSerializer):
    auction_like_count = serializers.SerializerMethodField()
    painting = PaintingDetailSerializer()
    seller = serializers.SerializerMethodField()
    
    def get_auction_like_count(self, obj):    
        return obj.auction_like.count()
    
    def get_seller(self, obj):
        return obj.seller.nickname

    class Meta:
        model = Auction
        fields = ('id', 'auction_like_count', 'painting', 'start_bid', 'now_bid', 'start_date', 'end_date', 'bidder', 'seller', )

#경매 입찰 serializer
class AuctionBidSerializer(serializers.ModelSerializer):

    class Meta:
        model = Auction
        fields = ('id', 'start_bid', 'now_bid', 'bidder', )

    def validate(self, data):
        auction = Auction.objects.get(id=self.instance.id)
        request_user = self.context.get("request").user
        user = User.objects.get(id=request_user.id)
                    
        start_bid = self.instance.start_bid         # 시작 입찰가
        now_bid = self.instance.now_bid             # 최고 입찰가
        enter_bid = data["now_bid"]                 # user가 front에 작성한 입찰가
        bidder = self.instance.bidder               # 최고 입찰가의 입찰자     

        # 소유자는 입찰 못하게함
        if request_user == auction.painting.owner:
            raise serializers.ValidationError(detail={"error": "소유자는 입찰 할 수 없습니다."})
            
        # 현재 입찰자와 최고가 입찰자 비교
        if request_user == bidder:
            raise serializers.ValidationError(detail={"error": "현재 이미 최고가로 입찰중입니다."})
        
        # 유저 보유포인트와 입찰가 비교
        if request_user.point < enter_bid:
            raise serializers.ValidationError(detail={"error": f"포인트가 부족합니다. 현재 보유중인 포인트는 {request_user.point} 입니다. 입찰가를 확인 해주세요."})
    
        # 100포인트 이상 입찰가 검사
        if enter_bid % 100 != 0:
            raise serializers.ValidationError(detail={"error": "100 포인트 단위로 입찰 가능합니다."})
        
        # 시작 입찰가와 입찰가 비교
        if enter_bid < start_bid:
            raise serializers.ValidationError(detail={"error": "시작 입찰가보다 적은 금액으로 입찰 하실 수 없습니다."})

        # 현재 입찰가와 입찰가 비교
        if enter_bid <= int(now_bid or 0):
            raise serializers.ValidationError(detail={"error": "현재 입찰가보다 같거나 적은 금액으로 입찰 하실 수 없습니다."})

        #입찰 재시도 전의 입찰가의 포인트를 돌려줌
        auction_history = AuctionHistory.objects.filter(auction=auction, bidder=request_user).order_by('-created_at')
        
        if auction_history: #경매 거래내역이 존재할 경우
            before_now_bid = auction_history[0].now_bid
            user.point += before_now_bid
            user.save()
        
        # 경매 거래 내역 저장
        AuctionHistory.objects.create(now_bid=enter_bid, bidder=request_user, auction=auction)
        
        #자기가 입력한 입찰가 포인트 차감
        user.point -= enter_bid
        user.save()

        return data

    def update(self, instance, validated_data):
        instance.now_bid = validated_data.get('now_bid', instance.now_bid)
        instance.bidder = validated_data.get('bidder', self.context.get("request").user) #현재 user가 bidder로 바뀜

        instance.save()

        return instance

#경매 거래내역 serializer
class AuctionHistoySerializer(serializers.ModelSerializer):
    bidder = serializers.SerializerMethodField()
    auction= serializers.SerializerMethodField()
    bidder_profile_image = serializers.SerializerMethodField()

    def get_bidder(self, obj):
        return obj.bidder.nickname

    def get_auction(self, obj):
        return obj.auction.painting.title

    def get_bidder_profile_image(self, obj):
        return obj.bidder.profile_image.url

    class Meta:
        model = AuctionHistory
        fields = ('id', 'bidder', 'auction', 'bidder_profile_image', 'now_bid', 'created_at', )

#경매 검색 serializer
class AuctionSearchSerializer(serializers.ModelSerializer):
    paintings = AuctionDetailSerializer()
    
    class Meta:
        model = Painting
        fields = ('id', 'paintings', )

#경매 댓글 serializer(상세, 리스트)
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
        fields = ('id', 'user', 'profile_image', 'auction', 'content', 'created_at', 'updated_at', )

#경매 댓글 생성 serializer
class AuctionCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content',)
        extra_kwargs = {'content':{
                        'error_messages': {
                        'required':'내용을 입력해주세요.',
                        'blank':'내용을 입력해주세요.',}},}
