from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from django.shortcuts import get_list_or_404

from paintings.models import Painting
from paintings.serializers import (PaintingListSerializer, PaintingCreateSerializer, ImageSerializer, 
                                PaintingDetailSerializer)
from .models import Painting, STYLE_CHOICES


#####유화#####
class PaintingListview(APIView):
    permission_classes = [IsAuthenticated]
    
    #유화 리스트
    def get(self, request):
        painting = get_list_or_404(Painting, author=request.user.id)        
        serializer = PaintingListSerializer(painting, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PaintingStyleSelectView(APIView):
    permission_classes = [IsAuthenticated]

    #유화 스타일 선택 페이지
    def get(self, requets):
        style = [[x, y] for x, y in STYLE_CHOICES]
        return Response(style, status=status.HTTP_200_OK)

class ImageUploadView(APIView):
    permission_classes = [IsAuthenticated]
    
    #유화 스타일 생성 페이지
    def get(self, requets):
        style = [[x, y] for x, y in STYLE_CHOICES]
        return Response(style, status=status.HTTP_200_OK)

    #이미지 업로드(before -> after)
    def post(self, request):
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaintingCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    #이미지 스타일 적용된 유화 생성(after)
    def put(self, request, painting_id):
        painting = get_object_or_404(Painting, id=painting_id)
        serializer = PaintingCreateSerializer(painting, data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaintingDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    #유화 상세페이지
    def get(self, request, painting_id):
        painting = get_object_or_404(Painting, id=painting_id)
        if request.user == painting.author:
            serializer = PaintingDetailSerializer(painting)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message":"접근 권한 없음"}, status=status.HTTP_403_FORBIDDEN)

    #유화 작품 수정
    def put(self, request, painting_id):        
        painting = get_object_or_404(Painting, id=painting_id)
        if request.user == painting.author:
            serializer = PaintingCreateSerializer(painting, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(owner=request.user, author=request.user, after_image=painting.after_image)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"접근 권한 없음"}, status=status.HTTP_403_FORBIDDEN)

    #유화 작품 삭제
    def delete(self, request, painting_id):        
        painting = get_object_or_404(Painting, id=painting_id)
        if request.user == painting.author:
            painting.delete()
            return Response({"message":"유화 삭제"}, status=status.HTTP_200_OK)
        return Response({"message":"접근 권한 없음"}, status=status.HTTP_403_FORBIDDEN)

