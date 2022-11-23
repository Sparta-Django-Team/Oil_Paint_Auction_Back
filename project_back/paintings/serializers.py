from rest_framework import serializers

from .models import Painting


class PaintingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Painting
        fields = "__all__"

class PaintingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Painting
        fields = "__all__"

