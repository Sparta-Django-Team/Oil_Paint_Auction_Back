# rest_framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# simple jwt
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# django
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_bytes, force_str
from django.contrib.auth import authenticate

# users
from users.models import User
from users.validators import (
    password_validator,
    repassword_validator,
    current_password_validator,
    nickname_validator,
    term_check_validator,
    check_token_validator,
)
from users.utils import Util

# auctions
from auctions.serializers import AuctionListSerializer

# User serializer (회원가입, 회원수정)
class UserSerializer(serializers.ModelSerializer):
    repassword = serializers.CharField(
        error_messages={
            "required": "비밀번호를 입력해주세요.",
            "blank": "비밀번호를 입력해주세요.",
        },
        write_only=True,
    )
    term_check = serializers.BooleanField(
        error_messages={
            "required": "약관동의를 확인해주세요.",
            "blank": "약관동의를 확인해주세요.",
        },
        write_only=True,
        validators=[term_check_validator],
    )

    class Meta:
        model = User
        fields = (
            "email",
            "nickname",
            "password",
            "repassword",
            "profile_image",
            "term_check",
        )
        extra_kwargs = {
            "email": {
                "error_messages": {
                    "required": "이메일을 입력해주세요.",
                    "invalid": "알맞은 형식의 이메일을 입력해주세요.",
                    "blank": "이메일을 입력해주세요.",
                },
                "validators": [
                    UniqueValidator(
                        queryset=User.objects.all(),
                        message="이미 사용중인 이메일 입니다.",
                    )
                ],
            },
            "nickname": {
                "error_messages": {
                    "required": "닉네임을 입력해주세요.",
                    "blank": "닉네임을 입력해주세요",
                    "unique": "이 이메일은 이미 사용 중입니다.",
                },
                "validators": [
                    nickname_validator,
                    UniqueValidator(
                        queryset=User.objects.all(),
                        message="이미 사용중인 닉네임 입니다.",
                    ),
                ],
            },
            "password": {
                "write_only": True,
                "error_messages": {
                    "required": "비밀번호를 입력해주세요.",
                    "blank": "비밀번호를 입력해주세요.",
                },
                "validators": [password_validator],
            },
        }

    def validate(self, data):
        password = data.get("password")
        repassword = data.get("repassword")

        repassword_validator(password, repassword)
        return data

    # 회원가입 create
    def create(self, validated_data):
        email = validated_data["email"]
        nickname = validated_data["nickname"]

        user = User(nickname=nickname, email=email)
        user.set_password(validated_data["password"])
        user.save()

        return user

    # 회원정보 수정 update
    def update(self, instance, validated_data):
        instance.nickname = validated_data.get("nickname", instance.nickname)
        instance.profile_image = validated_data.get("profile_image", instance.profile_image)
        instance.save()
        return instance


# 로그아웃 serializer
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            raise serializers.ValidationError(detail={"만료된 토큰": "유효하지 않거나 만료된 토큰입니다."})


# JWT serializer
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["nickname"] = user.nickname
        return token


# 비밀번호 변경 serializer
class PasswordChangeSerializer(serializers.ModelSerializer):
    repassword = serializers.CharField(
        error_messages={
            "required": "비밀번호를 입력해주세요.",
            "blank": "비밀번호를 입력해주세요.",
        },
        write_only=True,
    )

    class Meta:
        model = User
        fields = (
            "password",
            "repassword",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
                "error_messages": {
                    "required": "비밀번호를 입력해주세요.",
                    "blank": "비밀번호를 입력해주세요.",
                },
                "validators": [password_validator],
            },
        }

    def validate(self, data):
        current_password = self.context.get("request").user.password
        password = data.get("password")
        repassword = data.get("repassword")

        repassword_validator(password, repassword)
        current_password_validator(current_password, password)

        return data

    def update(self, instance, validated_data):
        instance.password = validated_data.get("password", instance.password)
        instance.set_password(instance.password)
        instance.save()
        return instance


# 비밀번호 찾기 serializer
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            "required": "이메일을 입력해주세요.",
            "blank": "이메일을 입력해주세요.",
            "invalid": "알맞은 형식의 이메일을 입력해주세요.",
        }
    )

    class Meta:
        fields = ("email",)

    def validate(self, attrs):
        try:
            email = attrs.get("email")

            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)

            frontend_site = "127.0.0.1:5500"
            absurl = f"http://{frontend_site}/set_password.html?/{uidb64}/{token}"

            email_body = "안녕하세요? \n 비밀번호 재설정 주소입니다.\n" + absurl
            message = {
                "email_body": email_body,
                "to_email": user.email,
                "email_subject": "비밀번호 재설정",
            }
            Util.send_email(message)

            return super().validate(attrs)

        except User.DoesNotExist:
            raise serializers.ValidationError(detail={"email": "잘못된 이메일입니다. 다시 입력해주세요."})


# 비밀번호 재설정 serializer
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        error_messages={
            "required": "비밀번호를 입력해주세요.",
            "blank": "비밀번호를 입력해주세요.",
        },
        write_only=True,
        validators=[password_validator],
    )
    repassword = serializers.CharField(
        error_messages={
            "required": "비밀번호를 입력해주세요.",
            "blank": "비밀번호를 입력해주세요.",
        },
        write_only=True,
    )
    token = serializers.CharField(
        max_length=100,
        write_only=True,
    )
    uidb64 = serializers.CharField(
        max_length=100,
        write_only=True,
    )

    class Meta:
        fields = (
            "repassword",
            "password",
            "token",
            "uidb64",
        )

    def validate(self, attrs):
        password = attrs.get("password")
        repassword = attrs.get("repassword")
        token = attrs.get("token")
        uidb64 = attrs.get("uidb64")

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)

            check_token_validator(user, token)
            repassword_validator(password, repassword)

            user.set_password(password)
            user.save()

            return super().validate(attrs)

        except User.DoesNotExist:
            raise serializers.ValidationError(detail={"user": "존재하지 않는 회원입니다."})


# User Token 획득
class TokenSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            "required": "이메일을 입력해주세요.",
            "blank": "이메일을 입력해주세요.",
            "invalid": "알맞은 형식의 이메일을 입력해주세요.",
        }
    )
    password = serializers.CharField(
        error_messages={
            "required": "비밀번호를 입력해주세요.",
            "blank": "비밀번호를 입력해주세요.",
        },
        write_only=True,
    )

    def validate(self, attrs):
        user = authenticate(email=attrs["email"], password=attrs["password"])
        user_email = self.context.get("request").user.email
        
        if user_email != attrs["email"]:
            raise serializers.ValidationError(detail={"email": "현재 사용자의 이메일과 요청된 이메일이 일치하지 않습니다."})
        
        if not user:
            raise serializers.ValidationError(detail={"user": "비밀번호가 일치하지 않습니다."})
        
        return attrs


# 프로필 serializer
class ProfileSerializer(serializers.ModelSerializer):
    like_auction = AuctionListSerializer(many=True)

    class Meta:
        model = User
        fields = (
            "email",
            "nickname",
            "profile_image",
            "point",
            "like_auction",
        )
