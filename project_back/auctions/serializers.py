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

