# rest_framework
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

# django
from django.utils import timezone
from django.db.models import Q, Prefetch, Count
from django.shortcuts import get_list_or_404
from django.core.exceptions import ValidationError

# swagger
from drf_yasg.utils import swagger_auto_schema

# auctions
from auctions.serializers import (
    AuctionCreateSerializer,
    AuctionListSerializer,
    AuctionDetailSerializer,
    AuctionCommentSerializer,
    AuctionCommentCreateSerializer,
    AuctionBidSerializer,
    AuctionSearchSerializer,
    AuctionHistoySerializer,
)
from auctions.models import Auction, Comment, AuctionHistory

# paintings
from paintings.models import Painting

# users
from users.models import User

# project_back
from project_back.permissions import IsOwner


#####경매#####
class AuctionListView(APIView):
    permissions_classes = [AllowAny]

    # 경매 리스트
    @swagger_auto_schema(
        operation_summary="전체 경매 리스트", 
        responses={200: "성공", 500: "서버 에러"}
    )
    def get(self, request):
        # 회원 활성화일 때만 가져오기
        active_users = User.objects.filter(is_active=True)
        
        # 마감되지 않은 경매 가져오기
        open_auctions = Auction.objects.filter(
            Q(end_date__gt=timezone.now()), seller__in=active_users
        ).annotate(auction_like_count=Count("auction_like"))
        
        # 마감임박 경매 가져오기
        closing_auctions = open_auctions.filter(
            Q(end_date__lt=timezone.now() + timezone.timedelta(days=1))
        ).order_by("end_date")

        # 모든 경매 가져오기
        auction = Auction.objects.filter(seller__in=active_users).annotate(auction_like_count=Count("auction_like"))

        # Prefetch 사용하여 관련 객체 미리 가져오기
        optimized_open_auctions = open_auctions.prefetch_related(
            Prefetch("painting"), Prefetch("auction_like"), Prefetch("bidder"), Prefetch("seller")
        )
        optimized_closing_auctions = closing_auctions.prefetch_related(
            Prefetch("painting"), Prefetch("auction_like"), Prefetch("bidder"), Prefetch("seller")
        )
        optimized_auction = auction.prefetch_related(
            Prefetch("painting"), Prefetch("auction_like"), Prefetch("bidder"), Prefetch("seller")
        )
        open_auctions_serializer = AuctionListSerializer(optimized_open_auctions, many=True).data
        closing_auction_serializer = AuctionListSerializer(optimized_closing_auctions, many=True).data
        auction_serializer = AuctionListSerializer(optimized_auction, many=True).data

        auction = {
            "open_auctions": open_auctions_serializer,
            "closing_auctions": closing_auction_serializer,
            "auction": auction_serializer,
        }
        return Response(auction, status=status.HTTP_200_OK)


class AuctionMyListView(APIView):
    permissions_classes = [IsAuthenticated]

    # 나의 경매 리스트
    @swagger_auto_schema(
        operation_summary="나의 경매 리스트",
        responses={200: "성공", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request):
        auction = get_list_or_404(Auction.objects.annotate(auction_like_count=Count("auction_like")), seller=request.user.id)
        serializer = AuctionListSerializer(auction, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuctionCreateView(APIView):
    permission_classes = [IsOwner]
    
    def get_objects(self, painting_id):
        painting = get_object_or_404(Painting, id=painting_id)
        self.check_object_permissions(self.request, painting)
        return painting

    # 경매 생성
    @swagger_auto_schema(
        request_body=AuctionCreateSerializer,
        operation_summary="경매 생성",
        responses={200: "성공", 400: "인풋값 에러", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def post(self, request, painting_id):
        painting = self.get_objects(painting_id)
        try:
            if Auction.objects.filter(painting=painting, seller=request.user.id).exists():
                raise ValidationError("이미 등록된 경매입니다.")

            serializer = AuctionCreateSerializer(data=request.data)
            serializer.is_valid()
            serializer.save(painting_id=painting_id, seller=request.user)

        except (ValidationError, Auction.DoesNotExist) as error:
            return Response({"message": str(error)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            painting.is_auction = True
            painting.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class AuctionDetailView(APIView):
    '''
    경매 낙찰 
    1. 낙찰이 되기 전 입찰한 사람이 없으면 낙찰 불가능 (해결)
    2. 낙찰이 되면 그림의 경매상태 False로 수정
    3. 낙찰이 안된 사람은 경매 내역을 보고 포인트 반환
    4. 경매 올린 소유주는 그 포인트만큼 주고, 소유주/판매자 변경(판매자는 null 값으로 변경)
    '''
    permissions_classes = [IsOwner]

    def get_objects(self, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)
        self.check_object_permissions(self.request, auction)
        return auction

    def get_permissions(self):
        if self.request.method == 'GET' or self.request.method == 'PUT':
            return [IsAuthenticated()]
        return [permission() for permission in self.permission_classes]

    def refund_points(self, auction):
        auction_history = AuctionHistory.objects.filter(auction=auction)
        bidders = auction_history.order_by("created_at").values("bidder", "now_bid")
        repayment_point = list({bidder["bidder"]: bidder for bidder in bidders}.values())
        sorted_repayment_point = sorted(repayment_point, key=lambda x: x["now_bid"])[:-1]

        for i in sorted_repayment_point:
            user = User.objects.get(id=i["bidder"])
            user.point += i["now_bid"]
            user.save()
    
    def give_points_to_owner(self, auction):
        last_bid = auction.now_bid
        before_owner = User.objects.get(email=auction.painting.owner)
        before_owner.point += last_bid
        before_owner.save()

    def change_owner_and_seller(self, auction):
        after_owner = auction.bidder
        painting = Painting.objects.get(id=auction.painting.id)
        painting.owner = after_owner
        auction.seller = None
        
        painting.save()
        auction.save()

    # 경매 낙찰
    @swagger_auto_schema(
        operation_summary="경매 낙찰",
        responses={200: "성공", 400: "조건 에러", 403: "접근 권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def post(self, request, auction_id):
        auction = self.get_objects(auction_id) 

        # 낙찰이 되기전 입찰한 사람이 없으면 낙찰 불가능
        if not auction.bidder:
            return Response({"message": "입찰한 사람이 없음"}, status=status.HTTP_400_BAD_REQUEST)
        
        self.refund_points(auction)
        self.give_points_to_owner(auction)
        self.change_owner_and_seller(auction)

        return Response({"message": "낙찰 완료"}, status=status.HTTP_200_OK)

    # 경매 상세페이지
    @swagger_auto_schema(
        operation_summary="경매 상세페이지",
        responses={200: "성공", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request, auction_id):
        auction = get_object_or_404(Auction.objects.filter(id=auction_id).annotate(auction_like_count=Count("auction_like")))
        serializer = AuctionDetailSerializer(auction)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 경매 현재 입찰가 등록 & 포인트 처리
    @swagger_auto_schema(
        request_body=AuctionBidSerializer,
        operation_summary="경매 입찰가 등록",
        responses={200: "성공", 400: "인풋값 에러", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def put(self, request, auction_id):
        auction = get_object_or_404(Auction.objects.select_related("painting").select_for_update() , id=auction_id)
        serializer = AuctionBidSerializer(auction, data=request.data, context={"request": request, "auction": auction})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 경매 삭제
    @swagger_auto_schema(
        operation_summary="경매 삭제",
        responses={200: "성공", 403: "접근 권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def delete(self, request, auction_id):
        auction = self.get_objects(auction_id)
        auction.delete()
        return Response({"message": "경매 삭제"}, status=status.HTTP_200_OK)


# 경매 좋아요
class AuctionLikeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="경매 좋아요", 
        responses={200: "성공", 404: "찾을 수 없음", 500: "서버 에러"}
    )
    def post(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)
        if request.user in auction.auction_like.all():
            auction.auction_like.remove(request.user)
            return Response({"message": "좋아요 취소되었습니다."}, status=status.HTTP_200_OK)
        else:
            auction.auction_like.add(request.user)
            return Response({"message": "좋아요 되었습니다."}, status=status.HTTP_200_OK)


class AuctionSearchView(APIView):
    permission_classes = [AllowAny]

    # 경매 검색
    @swagger_auto_schema(
        operation_summary="경매 검색", 
        responses={200: "성공", 500: "서버 에러"}
    )
    def get(self, request):
        query = request.GET.get("q")
        if query:
            auction_result = Painting.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query),
                is_auction=True,
            )
        serializer = AuctionSearchSerializer(auction_result, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuctionHistoryView(APIView):
    permission_classes = [AllowAny]

    # 경매 거래내역 표시
    @swagger_auto_schema(
        operation_summary="경매 거래내역", 
        responses={200: "성공", 500: "서버 에러"}
    )
    def get(self, request, auction_id):
        auction_history = AuctionHistory.objects.filter(auction=auction_id).order_by("-created_at")
        serializer = AuctionHistoySerializer(auction_history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


#####댓글#####
class CommentView(APIView):
    permission_classes = [IsAuthenticated]

    # 댓글 전체 조회
    @swagger_auto_schema(
        operation_summary="댓글 전체 조회",
        responses={200: "성공", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)
        comments = auction.comment.all()
        serializer = AuctionCommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 댓글 생성
    @swagger_auto_schema(
        request_body=AuctionCommentCreateSerializer,
        operation_summary="댓글 생성",
        responses={201: "성공", 400: "인풋값 에러", 500: "서버 에러"},
    )
    def post(self, request, auction_id):
        serializer = AuctionCommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, auction_id=auction_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    permission_classes = [IsOwner]

    def get_objects(self, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        self.check_object_permissions(self.request, comment)
        return comment

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [permission() for permission in self.permission_classes]

    # 댓글 조회 
    @swagger_auto_schema(
        operation_summary="댓글 상세 조회",
        responses={200: "성공", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request, auction_id, comment_id):
        comment = get_object_or_404(Comment, auction_id=auction_id, id=comment_id)
        serializer = AuctionCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 댓글 수정
    @swagger_auto_schema(
        request_body=AuctionCommentCreateSerializer,
        operation_summary="댓글 수정",
        responses={200: "성공", 400: "인풋값 에러", 403: "접근 권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def put(self, request, auction_id, comment_id):
        comment = self.get_objects(comment_id)
        serializer = AuctionCommentCreateSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, auction_id=auction_id)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 댓글 삭제
    @swagger_auto_schema(
        operation_summary="댓글 삭제",
        responses={200: "성공", 403: "접근 권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def delete(self, request, auction_id, comment_id):
        comment = self.get_objects(comment_id)
        comment.delete()
        return Response({"message": "댓글 삭제 완료"}, status=status.HTTP_200_OK)

