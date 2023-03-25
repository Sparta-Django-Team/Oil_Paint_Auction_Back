from rest_framework import serializers


class AuctionBidValidator:
    def validate_auction_status(self, auction):
        if auction.seller_id is None:
            raise serializers.ValidationError(detail={"error": "이미 종료된 경매입니다."})

    def validate_owner_cannot_bid(self, request_user, auction):
        if request_user.id == auction.painting.owner_id:
            raise serializers.ValidationError(detail={"error": "소유자는 입찰 할 수 없습니다."})

    def validate_not_highest_bidder(self, request_user, bidder_id):
        if request_user.id == bidder_id:
            raise serializers.ValidationError(detail={"error": "현재 이미 최고가로 입찰중입니다."})

    def validate_sufficient_points(self, request_user, enter_bid):
        if request_user.point < enter_bid:
            raise serializers.ValidationError(
                detail={"error": f"포인트가 부족합니다. 현재 보유중인 포인트는 {request_user.point} 입니다. 입찰가를 확인 해주세요."})

    def validate_bid_increment(self, enter_bid):
        if enter_bid % 100 != 0:
            raise serializers.ValidationError(detail={"error": "100 포인트 단위로 입찰 가능합니다."})

    def validate_enter_bid_against_start_bid(self, enter_bid, start_bid):
        if enter_bid < start_bid:
            raise serializers.ValidationError(detail={"error": "시작 입찰가보다 적은 금액으로 입찰 하실 수 없습니다."})

    def validate_enter_bid_against_now_bid(self, enter_bid, now_bid):
        if enter_bid <= int(now_bid or 0):
            raise serializers.ValidationError(detail={"error": "현재 입찰가보다 같거나 적은 금액으로 입찰 하실 수 없습니다."})
