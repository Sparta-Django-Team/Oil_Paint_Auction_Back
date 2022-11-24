

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from paintings.models import Painting
from paintings.serializers import PaintingSerializer, PaintingCreateSerializer, ImageSerializer


from .models import Painting, STYLE_CHOICES
from users.models import User


import json

# Create your views here.
class PaintingStyleSelectView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, requets):
        style = [[x, y] for x, y in STYLE_CHOICES]
        return Response(style, status=status.HTTP_200_OK)

class PaintingCreateView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, requets):
        style = [[x, y] for x, y in STYLE_CHOICES]
        return Response(style, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, painting_id):
        painting = get_object_or_404(Painting, id=painting_id)
        serializer = PaintingCreateSerializer(painting, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# class PaintingCreateView(APIView):
#     # permission_classes = [IsAuthenticated]
#     def get(self, requets):
#         style = [[x, y] for x, y in STYLE_CHOICES]
#         return Response(style, status=status.HTTP_200_OK)

#     def put(self, request, painting_id):
#         painting = get_object_or_404(Painting, id=painting_id)
#         serializer = PaintingCreateSerializer(painting, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)








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

