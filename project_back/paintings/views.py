
from django.shortcuts import get_list_or_404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from paintings.models import Painting, PaintStyle
from paintings.serializers import StyleSerializer, PaintingCreateSerializer


# Create your views here.
class PaintingStyleSelectView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        styles = get_list_or_404(PaintStyle)
        serializer = StyleSerializer(styles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        pass


class PaintingCreateView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, style_no):
        pass

    def post(self, request):
        pass
