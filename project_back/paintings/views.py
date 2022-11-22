
from django.shortcuts import get_list_or_404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from paintings.models import Painting, PaintStyle



# Create your views here.
class PaintingStyleSelectView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        pass

    def post(self, request):
        pass


class PaintingCreateView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, style_no):
        pass

    def post(self, request):
        pass
