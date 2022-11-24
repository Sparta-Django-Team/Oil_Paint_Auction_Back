from rest_framework import serializers

from auctions.models import Auction, Comment
from paintings.serializers import PaintingDetailSerializer

class AuctionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ('start_bid', 'end_date',)

class AuctionListSerializer(serializers.ModelSerializer):
    auction_like = serializers.StringRelatedField(many=True)
    auction_like_count = serializers.SerializerMethodField()
    painting = PaintingDetailSerializer()

    def get_auction_like_count(self, obj) :    
        return obj.auction_like.count()

    class Meta:
        model = Auction
        fields = "__all__"

class AuctionDetailSerializer(serializers.ModelSerializer):
    auction_like = serializers.StringRelatedField(many=True)
    auction_like_count = serializers.SerializerMethodField()
    painting = PaintingDetailSerializer()

    def get_auction_like_count(self, obj) :    
        return obj.auction_like.count()

    class Meta:
        model = Auction
        fields = "__all__"


class AuctionCommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    auction = serializers.StringRelatedField()

    def get_user(self, obj):
        return obj.user.nickname

    def get_profile_image(self, obj):
        return obj.user.profile_image.url

    class Meta:
        model = Comment
        fields = "__all__"