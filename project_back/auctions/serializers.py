from rest_framework import serializers

from auctions.models import Auction 
from paintings.models import Painting

class MyPageserializer(serializers.ModelSerializer):

    class Meta:
        model = Painting
        fields = "__all__"

class AuctionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ("start_bid","end_date",)

class paintingserializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    def get_author(self, obj):
         return obj.author.nickname

    def get_owner(self, obj):
         return obj.owner.nickname

    class Meta:
        model = Painting
        fields = ('id', 'title', 'content', 'author', 'owner', 'after_image')

class AuctionListSerializer(serializers.ModelSerializer):
    auction_like = serializers.StringRelatedField(many=True)
    auction_like_count = serializers.SerializerMethodField()
    painting = paintingserializer()

    def get_auction_like_count(self, obj) :    
        return obj.auction_like.count()

    class Meta:
        model = Auction
        fields = "__all__"

class AuctionDetailSerializer(serializers.ModelSerializer):
    auction_like = serializers.StringRelatedField(many=True)
    auction_like_count = serializers.SerializerMethodField()
    painting = paintingserializer()

    def get_auction_like_count(self, obj) :    
        return obj.auction_like.count()

    class Meta:
        model = Auction
        fields = "__all__"

