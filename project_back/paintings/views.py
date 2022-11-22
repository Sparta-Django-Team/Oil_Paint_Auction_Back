from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from paintings.models import Painting
from paintings.serializers import PaintingSerializer
from rest_framework import status

class PaintingDetailView(APIView):

    #유화 작품 수정
    def put(self, request, painting_id, format=None):
        painting = get_object_or_404(Painting, id=painting_id)
        serializer = PaintingSerializer(painting, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"수정 완료!"},serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message":"수정 불가!"},serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #유화 작품 삭제
    def delete(self, request, painting_id, format=None):
        painting = get_object_or_404(Painting, id=painting_id)
        painting.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
