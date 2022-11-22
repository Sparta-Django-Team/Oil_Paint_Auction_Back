from rest_framework import serializers

from auctions.models import Auction


class MyPageserializer(serializers.Modelserializer):
    class Meta:
        model = Painting
        fields = '__all__'


class AuctionCreateSerializer(serializers.Modelserializer):
    class Meta:
        model = Auction
        fields = ("start_bid","end_date",)

