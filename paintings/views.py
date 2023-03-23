# rest_framework
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser

# django
from django.shortcuts import get_list_or_404

# swagger
from drf_yasg.utils import swagger_auto_schema

# project_back
from project_back.permissions import IsOwner

# paintings
from .models import Painting
from .serializers import (
    PaintingListSerializer,
    PaintingCreateSerializer,
    ImageSerializer,
    PaintingDetailSerializer,
)
from .models import Painting, STYLE_CHOICES


####유화#####
class PaintingStyleSelectView(APIView):
    permission_classes = [IsAuthenticated]

    # 유화 스타일 선택
    @swagger_auto_schema(
        operation_summary="유화 스타일 선택", 
        responses={200: "성공", 500: "서버 에러"}
    )
    def get(self, requets):
        style = [[x, y] for x, y in STYLE_CHOICES]
        return Response(style, status=status.HTTP_200_OK)


class ImageUploadView(APIView):
    permission_classes = [IsAuthenticated]

    # 유화 스타일 생성
    @swagger_auto_schema(
        operation_summary="유화 스타일 생성", 
        responses={200: "성공", 500: "서버 에러"}
    )
    def get(self, requets):
        style = [[x, y] for x, y in STYLE_CHOICES]
        return Response(style, status=status.HTTP_200_OK)

    # 이미지 업로드(before -> after)
    @swagger_auto_schema(
        request_body=ImageSerializer,
        operation_summary="유화 이미지 업로드(before -> after)",
        responses={200: "성공", 400: "인풋값 에러", 500: "서버 에러"},
    )
    def post(self, request):
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaintingListview(APIView):
    permission_classes = [IsAuthenticated]

    # 유화 리스트
    @swagger_auto_schema(
        operation_summary="유화 리스트", 
        responses={200: "성공", 404: "찾을 수 없음", 500: "서버 에러"}
    )
    def get(self, request):
        painting = get_list_or_404(Painting, owner=request.user.id)
        serializer = PaintingListSerializer(painting, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PaintingDetailView(APIView):
    permission_classes = [IsOwner]

    def get_objects(self, painting_id):
        painting = get_object_or_404(Painting, id=painting_id)
        self.check_object_permissions(self.request, painting)
        return painting

    # 유화 상세페이지
    @swagger_auto_schema(
        operation_summary="유화 상세페이지",
        responses={200: "성공", 403: "접근 권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request, painting_id):
        painting = self.get_objects(painting_id)
        serializer = PaintingDetailSerializer(painting)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 이미지 스타일 적용된 유화 생성(after)
    @swagger_auto_schema(
        request_body=PaintingCreateSerializer,
        operation_summary="이미지 스타일 적용된 유화 생성",
        responses={201: "성공", 400: "인풋값 에러", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def post(self, request, painting_id):
        painting = get_object_or_404(Painting, id=painting_id)
        serializer = PaintingCreateSerializer(painting, data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 유화 작품 수정
    @swagger_auto_schema(
        request_body=PaintingCreateSerializer,
        operation_summary="유화 작품 수정",
        responses={200: "성공", 400: "인풋값 에러", 403: "접근 권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def put(self, request, painting_id):
        painting = self.get_objects(painting_id)
        serializer = PaintingCreateSerializer(painting, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(owner=request.user, author=request.user, after_image=painting.after_image)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 유화 작품 삭제
    @swagger_auto_schema(
        operation_summary="유화 작품 삭제",
        responses={200: "성공", 403: "접근 권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def delete(self, request, painting_id):
        painting = self.get_objects(painting_id)
        painting.delete()
        return Response({"message": "유화 삭제"}, status=status.HTTP_200_OK)
