from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_list_or_404

from drf_yasg.utils import swagger_auto_schema

from .serializers import (AuctionCreateSerializer, AuctionListSerializer, AuctionDetailSerializer, 
                        AuctionCommentSerializer, AuctionCommentCreateSerializer, AuctionBidSerializer, 
                        AuctionSearchSerializer, AuctionHistoySerializer)
from .models import Auction, Comment, AuctionHistory
from paintings.models import Painting
from users.models import User


#####경매#####
class AuctionListView(APIView):
    permissions_classes = [AllowAny] 

    #경매 리스트
    @swagger_auto_schema(operation_summary="전체 경매 리스트", 
                        responses={ 200 : '성공', 500:'서버 에러'})
    def get(self, request): 
        
        #모든 경매 가져오기(회원 활성화 일 때 가져옴)
        auction = Auction.objects.filter(painting__owner__status__in=["N", "S"])
        
        #마감되지 않은 경매 가져오기(회원 활성화 일 때 가져옴)
        open_auctions = Auction.objects.filter(Q(end_date__gt=timezone.now()), painting__owner__status__in=["N", "S"] ).exclude(seller__isnull=True)

        #마감임박 경매 가져오기(회원 활성화 일 때 가져옴)
        closing_auctions = open_auctions.filter(Q(end_date__lt=timezone.now()+timezone.timedelta(days=1))).order_by('end_date')
        
        open_auctions_serializer = AuctionListSerializer(open_auctions, many=True).data
        closing_auction_serializer = AuctionListSerializer(closing_auctions, many=True).data
        auction_serializer = AuctionListSerializer(auction, many=True).data
        
        auction = {
            "open_auctions": open_auctions_serializer, 
            "closing_auctions": closing_auction_serializer,
            "auction" : auction_serializer 
        }     
        return Response(auction, status=status.HTTP_200_OK)
    
class AuctionMyListView(APIView):
    permissions_classes = [IsAuthenticated] 

    #나의 경매 리스트
    @swagger_auto_schema(operation_summary="나의 경매 리스트", 
                        responses={ 200 : '성공', 404 : '찾을 수 없음', 500:'서버 에러'})
    def get(self, request):
        auction = get_list_or_404(Auction,seller=request.user.id)
        serializer = AuctionListSerializer(auction, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AuctionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    # 경매 생성
    @swagger_auto_schema(request_body=AuctionCreateSerializer, 
                        operation_summary="경매 생성", 
                        responses={ 200 : '성공', 400:'인풋값 에러', 404:'찾을 수 없음', 500:'서버 에러'})
    def post(self, request, painting_id):
        painting = get_object_or_404(Painting, id=painting_id)

        #존재하는 경매가 있으면 에러발생
        if Auction.objects.filter(painting=painting, seller=request.user.id).exists():
            return Response({"message":"이미 등록된 경매입니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = AuctionCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(painting_id=painting_id, seller=request.user)
            painting.is_auction = True
            painting.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuctionDetailView(APIView):
    permissions_classes = [AllowAny] 

    # 경매 낙찰
    @swagger_auto_schema(operation_summary="경매 낙찰", 
                        responses={ 200 : '성공', 400:'조건 에러', 403:'접근 권한 없음', 404:'찾을 수 없음', 500:'서버 에러'})
    def post(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)

        if request.user == auction.painting.owner:
            #낙찰이 되기전 입찰한 사람이 없으면 낙찰 불가능 
            if not auction.bidder:            
                return Response({"message":"입찰한 사람이 없음"}, status=status.HTTP_400_BAD_REQUEST) 

            #낙찰이 되면
            auction.painting.is_auction = False
            auction.save()

            #낙찰이 안된 사람은 포인트 반환
            auction_history = AuctionHistory.objects.filter(auction=auction)

            bidders = auction_history.order_by("created_at").values('bidder','now_bid')
            repayment_point = list({bidder['bidder']: bidder for bidder in bidders}.values())
            sorted_repayment_point = sorted(repayment_point , key= lambda x: x['now_bid'])[:-1]

            for i in sorted_repayment_point:
                user = User.objects.get(id=i["bidder"])
                user.point += i["now_bid"]

                user.save()
            
            #경매에 올린 소유주는 그 포인트만큼 줌, 소유주/판매자 변경
            last_bid = auction.now_bid
            before_owner =  User.objects.get(email=auction.painting.owner)

            before_owner.point += last_bid # 포인트 돌려줌
            before_owner.save() 

            after_owner = auction.bidder
            painting = Painting.objects.get(id=auction.painting.id)
            painting.owner = after_owner # 소유주 변경 
            auction.seller = None # 판매자 null 값
            
            auction.save()
            painting.save()

            return Response({"message":"낙찰 완료"}, status=status.HTTP_200_OK) 
        return Response({"message":"접근 권한 없음"}, status=status.HTTP_403_FORBIDDEN) 

    # 경매 상세페이지
    @swagger_auto_schema(operation_summary="경매 상세페이지", 
                        responses={ 200 : '성공', 404:'찾을 수 없음', 500:'서버 에러'})
    def get(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id, painting__owner__status__in=["N", "S"])
        serializer = AuctionDetailSerializer(auction)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 경매 현재 입찰가 등록 & 포인트 처리
    @swagger_auto_schema(request_body=AuctionBidSerializer, 
                        operation_summary="경매 입찰가 등록", 
                        responses={ 200 : '성공',  400:'인풋값 에러', 403:'접근 권한 없음', 404:'찾을 수 없음', 500:'서버 에러'})
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
    @swagger_auto_schema(operation_summary="경매 삭제", 
                        responses={ 200 : '성공', 403:'접근 권한 없음', 404:'찾을 수 없음', 500:'서버 에러'})
    def delete(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)
        if request.user == auction.painting.owner:
            auction.delete()
            return Response({"message":"경매 삭제"}, status=status.HTTP_200_OK)
        return Response({"message":"접근 권한 없음"}, status=status.HTTP_403_FORBIDDEN) 

# 경매 좋아요
class AuctionLikeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="경매 좋아요", 
                        responses={ 200 : '성공', 404:'찾을 수 없음', 500:'서버 에러'})
    def post(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)
        if request.user in auction.auction_like.all():
            auction.auction_like.remove(request.user)
            return Response({"message":"좋아요 취소되었습니다."}, status=status.HTTP_200_OK)
        else:
            auction.auction_like.add(request.user)
            return Response({"message":"좋아요 되었습니다."}, status=status.HTTP_200_OK)

class AuctionSearchView(APIView):
    permission_classes = [AllowAny]

    #경매 검색
    @swagger_auto_schema(operation_summary="경매 검색", 
                        responses={ 200 : '성공', 500:'서버 에러'})
    def get(self, request):
        search = request.GET.get('search')
        if search:
            auction_result = Painting.objects.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) 
            , is_auction =True, painting__owner__status__in=["N", "S"]
            )
        serializer = AuctionSearchSerializer(auction_result, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AuctionHistoryView(APIView):
    permission_classes = [AllowAny]

    # 경매 거래내역 표시
    @swagger_auto_schema(operation_summary="경매 거래내역", 
                        responses={ 200 : '성공', 500:'서버 에러'})
    def get(self, request, auction_id):
        auction_history = AuctionHistory.objects.filter(auction=auction_id).order_by('-created_at')
        serializer = AuctionHistoySerializer(auction_history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#####댓글#####
class CommentView(APIView):
    permission_classes = [IsAuthenticated]

    # 댓글 전체 조회
    @swagger_auto_schema(operation_summary="댓글 전체 조회", 
                        responses={ 200 : '성공', 404:'찾을 수 없음', 500:'서버 에러'})
    def get(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id, painting__owner__status__in=["N", "S"])
        comments = auction.comment.all()
        serializer = AuctionCommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 댓글 생성
    @swagger_auto_schema(request_body=AuctionCommentCreateSerializer, operation_summary="댓글 생성", 
                        responses={ 201 : '성공', 400:'인풋값 에러', 500:'서버 에러'})
    def post(self, request, auction_id):
        serializer = AuctionCommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, auction_id=auction_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    #댓글 조회
    @swagger_auto_schema(operation_summary="댓글 상세 조회", 
                        responses={ 200 : '성공', 404:'찾을 수 없음', 500:'서버 에러'})
    def get(self, request, auction_id, comment_id):
        auction = get_object_or_404(Auction, id=auction_id, painting__owner__status__in=["N", "S"])
        comment = get_object_or_404(Comment, auction_id=auction, id=comment_id)
        serializer = AuctionCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #댓글 수정
    @swagger_auto_schema(request_body=AuctionCommentCreateSerializer, operation_summary="댓글 수정", 
                        responses={ 200 : '성공', 400:'인풋값 에러', 403:'접근 권한 없음', 404:'찾을 수 없음', 500:'서버 에러'})
    def put(self, request, auction_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.user:
            serializer = AuctionCommentCreateSerializer(comment, data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, auction_id=auction_id)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"접근 권한 없음"}, status=status.HTTP_403_FORBIDDEN)

    # 댓글 삭제
    @swagger_auto_schema(operation_summary="댓글 삭제", 
                        responses={ 200 : '성공', 403:'접근 권한 없음', 404:'찾을 수 없음', 500:'서버 에러'})
    def delete(self, request, auction_id, comment_id):
        comment= get_object_or_404(Comment, id=comment_id)
        if request.user == comment.user:
            comment.delete()
            return Response({"message":"댓글 삭제 완료"},status=status.HTTP_200_OK)
        return Response({"message":"접근 권한 없음"}, status=status.HTTP_403_FORBIDDEN)
