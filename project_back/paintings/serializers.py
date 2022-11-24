from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import serializers

from .models import Painting
from users.models import User

from .styler import painting_styler


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Painting
        fields = ("id","style","before_image",)

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


    class Meta:
        model = Painting
        fields = ("title", "content", "owner", "author", "after_image", )
        extra_kwargs = {'title': {
                        'error_messages': {
                        'required': '제목을 입력해주세요',
                        'blank':'제목을 입력해주세요',}},

                        'content':{
                        'error_messages': {
                        'required':'내용을 입력해주세요.',
                        'blank':'내용을 입력해주세요.',}},
                        }

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.owner = validated_data.get('user_id', validated_data["owner"])
        instance.author = validated_data.get('user_id', validated_data["author"])
        instance.after_image = painting_styler(instance.before_image, instance.style)
        instance.save()

        return instance


class PaintingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Painting
        fields = "__all__"

