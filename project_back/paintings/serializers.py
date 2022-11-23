from rest_framework import serializers

from .models import Painting


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Painting
        fields = '__all__'

    def create(self, validated_data):
        title = validated_data['title']
        content = validated_data['content']
        style = validated_data['style_i']
        before_image = validated_data['upload_img']
        painting= Painting(
            title=title,
            content=content,
            style=style,
            before_image=before_image
        )
        painting.save()
    

class PaintingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Painting
        fields = "__all__"

class PaintingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Painting
        fields = "__all__"

