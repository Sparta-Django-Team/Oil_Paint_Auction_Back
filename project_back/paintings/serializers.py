from rest_framework import serializers

from .models import Painting, PaintStyle


class StyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaintStyle
        fields = ('model_name', 'model_urls',)


class PaintingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Painting
        fields = "__all__"

class PaintingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Painting
        fields = "__all__"

