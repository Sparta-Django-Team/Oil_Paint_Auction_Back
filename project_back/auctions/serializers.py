from rest_framework import serializers

from auctions.models import Auction
from paintings.serializers import PaintingSerializer
class AuctionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ('start_bid', 'end_date',)

class AuctionListSerializer(serializers.ModelSerializer):
    auction_like = serializers.StringRelatedField(many=True)
    auction_like_count = serializers.SerializerMethodField()
    painting = PaintingSerializer()

    def get_auction_like_count(self, obj) :    
        return obj.auction_like.count()

    class Meta:
        model = Auction
        fields = "__all__"

class AuctionDetailSerializer(serializers.ModelSerializer):
    auction_like = serializers.StringRelatedField(many=True)
    auction_like_count = serializers.SerializerMethodField()
    painting = PaintingSerializer()

    def get_auction_like_count(self, obj) :    
        return obj.auction_like.count()

    class Meta:
        model = Auction
        fields = "__all__"

