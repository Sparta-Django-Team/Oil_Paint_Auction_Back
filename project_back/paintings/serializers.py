from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import serializers

from .models import Painting
from .styler import painting_styler

import sys


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Painting
        fields = ("style","before_image",)

    def create(self, validated_data):
        style_no = validated_data["style"]
        before_image = validated_data['before_image']

        painting= Painting(
            style=style_no,
            before_image=before_image,
        )
        painting.save()
        return painting


class PaintingCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(error_messages={'required':'제목을 입력해주세요.', 'blank':'제목을 입력해주세요.'})
    # content = serializers.TextField(error_messages={'required':'내용을 입력해주세요.', 'blank':'내용을 입력해주세요.'})

    class Meta:
        model = Painting
        fields = ("title", "content", "owner", "author", )

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.owner = validated_data.get('owner', instance.owner)
        instance.author = validated_data.get('author', instance.author)
        instance.save()

        return instance


class PaintingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Painting
        fields = "__all__"

