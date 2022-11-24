from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.db import IntegrityError

from .serializers import AuctionCreateSerializer, AuctionListSerializer, AuctionDetailSerializer
from .models import Auction

#####경매#####
class AuctionListView(APIView):
    permissions_classes = [AllowAny] 
    
    #경매 리스트
    def get(self, request):
        auction = Auction.objects.all()
        serializer = AuctionListSerializer(auction, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AuctionCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    #경매 생성
    def post(self, request, painting_id): 
        serializer = AuctionCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(painting_id=painting_id)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            except IntegrityError as e:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuctionDetailView(APIView):
    permissions_classes = [AllowAny] 
    
    # 경매 상세 조회
    def get(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)
        serializer = AuctionDetailSerializer(auction)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 경매 삭제
    def delete(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)
        if request.user == auction.painting.author:
            auction.delete()
            return Response({"message":"경매 삭제"}, status=status.HTTP_200_OK)
        return Response({"message":"접근 권한 없음"}, status=status.HTTP_403_FORBIDDEN) 

#경매 좋아요
class AuctionLikeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)
        if request.user in auction.auction_like.all():
            auction.auction_like.remove(request.user)
            return Response({"message":"좋아요 취소되었습니다."}, status=status.HTTP_200_OK)
        else:
            auction.auction_like.add(request.user)
            return Response({"message":"좋아요 되었습니다."}, status=status.HTTP_200_OK)


