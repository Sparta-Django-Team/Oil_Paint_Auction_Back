from rest_framework import serializers

from auctions.models import Auction, Comment
from paintings.serializers import PaintingDetailSerializer

class AuctionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ('start_bid', 'end_date',)
        extra_kwargs = {'start_bid':{
                        'error_messages': {
                        'required':'입찰가를 입력해주세요.',
                        'blank':'입찰가를 입력해주세요.',}},
                        
                        'end_date':{
                        'error_messages': {
                        'required':'날짜를 입력해주세요.',
                        'blank':'날짜를 입력해주세요.',}},
                        }

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

class AuctionCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content',)
        extra_kwargs = {'content':{
                        'error_messages': {
                        'required':'내용을 입력해주세요.',
                        'blank':'내용을 입력해주세요.',}},}