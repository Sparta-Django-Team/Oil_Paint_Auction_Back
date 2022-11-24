from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.shortcuts import get_list_or_404

from .serializers import MyPageserializer,AuctionCreateSerializer, AuctionListSerializer, AuctionDetailSerializer
from .models import Painting, Auction


#유화 리스트페이지
class MyPageView(APIView):
    permission_classes = [IsAuthenticated] 
    def get(self, request):
        painting = get_list_or_404(Painting, author=request.user.id)        
        serializer = MyPageserializer(painting, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 경매 전체 리스트
class AuctionAlllistView(APIView):
    permissions_classes = [AllowAny] 
    def get(self, request):
        auction = Auction.objects.all()
        serializer = AuctionListSerializer(auction, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 경매 상세 조회
class AuctionDetailView(APIView):
    permissions_classes = [AllowAny] 
    def get(self, request,user_id, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)
        serializer = AuctionDetailSerializer(auction)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 경매 삭제
    def delete(self, request, user_id, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)
        if request.user == auction.painting.author:
            auction.delete()
            return Response(status=status.HTTP_200_OK)
        return Response("접근 권한 없음", status=status.HTTP_403_FORBIDDEN) 


#경매 생성
class AuctionListView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request,painting_id): 
        serializer = AuctionCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(painting_id=painting_id)
            return Response(serializer.data,status=status.HTTP_200_OK)       
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


#경매 좋아요
class LikeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request,auction_id):
        auction = get_object_or_404(Auction, id=auction_id)
        if request.user in auction.auction_like.all():
            auction.auction_like.remove(request.user)
            return Response('좋아요 취소되었습니다.',status=status.HTTP_200_OK)
        else:
            auction.auction_like.add(request.user)
            return Response('좋아요 되었습니다.',status=status.HTTP_200_OK)
