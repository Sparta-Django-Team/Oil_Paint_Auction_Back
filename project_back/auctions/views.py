from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.utils import timezone
from django.db import IntegrityError
from django.shortcuts import get_list_or_404

from .serializers import (AuctionCreateSerializer, AuctionListSerializer, AuctionDetailSerializer, 
                        AuctionCommentSerializer, AuctionCommentCreateSerializer, AuctionBidSerializer, AuctionHistoySerializer)
from .models import Auction, Comment, AuctionHistory



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

    #경매 상세페이지
    def get(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)
        # 마감 날짜 확인
        if auction.end_date > timezone.now():
            serializer = AuctionDetailSerializer(auction)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message":"경매가 마감되었습니다."},status=status.HTTP_400_BAD_REQUEST)

    #경매 현재 입찰가 등록
    def put(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)
        if request.user:
            serializer = AuctionBidSerializer(auction, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data , status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"접근 권한 없음"}, status=status.HTTP_403_FORBIDDEN) 
    
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
        
class AuctionHistoryView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, auction_id):
        auction_history = get_list_or_404(AuctionHistory, auction=auction_id)
        serializer = AuctionHistoySerializer(auction_history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

#####댓글#####
class CommentView(APIView):
    permission_classes = [IsAuthenticated]

    # 댓글 조회
    def get(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)
        comments = auction.comment.all()
        serializer = AuctionCommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 댓글 생성
    def post(self, request, auction_id):
        serializer = AuctionCommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, auction_id=auction_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    #댓글 수정
    def put(self, request, auction_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.user:
            serializer = AuctionCommentCreateSerializer(comment, data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, auction_id=auction_id)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"접근 권한 없음"}, status=status.HTTP_403_FORBIDDEN)

    #댓글 삭제
    def delete(self, request, auction_id, comment_id):
        comment= get_object_or_404(Comment, id=comment_id)
        if request.user == comment.user:
            comment.delete()
            return Response({"message":"댓글 삭제 완료"},status=status.HTTP_200_OK)
        return Response({"message":"접근 권한 없음"}, status=status.HTTP_403_FORBIDDEN)