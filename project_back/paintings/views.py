from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status

from .models import Painting
from .serializers import PaintingSerializer
class PaintingDetailView(APIView):

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
    
