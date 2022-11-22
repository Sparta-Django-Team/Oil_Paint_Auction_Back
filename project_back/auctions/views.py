from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from auctions.serializers import MyPageserializer,AuctionCreateSerializer

from django.shortcuts import get_list_or_404

from .models import Painting, Auction



class MyPageView(APIView):
    #유화 리스트페이지
    def get(self, request, user_id):
        painting = get_list_or_404(Painting, author=user_id)
        serializer = MyPageserializer(painting, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class AuctionListView(APIView):
    def post(self,request,painting_id):
        serializer = AuctionCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user,print_id=painting_id)
            return Response(serializer.data,status=status.HTTP_200_OK)       
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
# 1. id 값으로 전달해서 가져온다
# 2. print이미지, 제목, 내용 가져오고 시작가만 작성


class LikeView(APIView):
    def post(self,request,auction_id):
        auction = get_object_or_404(Auction,id=auction_id)
        if request.user in auction.auction_like.all():
            auction.likes.remove(request.user)
            return Response('좋아요 취소되었습니다.',status=status.HTTP_200_OK)
        else:
            auction.likes.add(request.user)
            return Response('좋아요 되었습니다.',status=status.HTTP_200_OK)