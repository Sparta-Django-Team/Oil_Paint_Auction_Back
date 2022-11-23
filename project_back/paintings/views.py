from django.shortcuts import get_list_or_404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from paintings.models import Painting
from paintings.serializers import PaintingSerializer, PaintingCreateSerializer, ImageSerializer

from .styler import painting_styler
from .models import Painting, STYLE_CHOICES


import json

# Create your views here.
class PaintingStyleSelectView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, requets):
        style = [[x, y] for x, y in STYLE_CHOICES]
        return Response(style, status=status.HTTP_200_OK)

class ImageUploadView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, requets):
        style = [[x, y] for x, y in STYLE_CHOICES]
        return Response(style, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        print(request.user)
        temp_img = Painting()
        temp_img.before_image = request.FILES.get('image')
        temp_img.author_id = request.user.id
        temp_img.owner_id = request.user.id
        temp_img.style = STYLE_CHOICES[0][0]

        painting_url = temp_img.before_image
        style_id = temp_img.style
        print("-----painting_id------")
        print(painting_url)
        print(style_id)
        style_no = STYLE_CHOICES[0]
        img_path = painting_styler(painting_url, style_no)
        temp_img.after_image = img_path
        temp_img.save()

        return Response({"img_path":img_path, "message":"변환 완료", 'painting_id':temp_img.id}, status=status.HTTP_200_OK)

class PaintingCreateView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, requets):
        style = [[x, y] for x, y in STYLE_CHOICES]
        return Response(style, status=status.HTTP_200_OK)

    def put(self, request, painting_id):
        painting = get_object_or_404(Painting, id=painting_id)
        if request.user == painting.owner:
            serializer = PaintingCreateSerializer(painting, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다!", status=status.HTTP_403_FORBIDDEN)

class PaintingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    #유화 작품 수정
    def put(self, request, painting_id):        
        painting = get_object_or_404(Painting, id=painting_id)
        if request.user == painting.author:
            serializer = PaintingSerializer(painting, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response("접근 권한 없음", status=status.HTTP_403_FORBIDDEN)

    #유화 작품 삭제
    def delete(self, request, painting_id):        
        painting = get_object_or_404(Painting, id=painting_id)
        if request.user == painting.author:
            painting.delete()
            return Response(status=status.HTTP_200_OK)
        return Response("접근 권한 없음", status=status.HTTP_403_FORBIDDEN)

