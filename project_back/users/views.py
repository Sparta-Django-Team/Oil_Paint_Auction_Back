# rest_framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import AuthenticationFailed

# simple jwt
from rest_framework_simplejwt.views import TokenObtainPairView

# django
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import DjangoUnicodeDecodeError, force_str
from django.contrib.auth import authenticate

# swagger
from drf_yasg.utils import swagger_auto_schema

# users
from .serializers import (
    UserSerializer,
    LogoutSerializer,
    CustomTokenObtainPairSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
    SetNewPasswordSerializer,
    TokenSerializer,
    ProfileSerializer,
)
from .models import User
from .authentication import ConfirmTokenAuthentication

# project
from project_back.permissions import IsOwner


# 회원가입
class SignupView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=UserSerializer,
        operation_summary="회원가입",
        responses={201: "성공", 400: "인풋값 에러", 500: "서버 에러"},
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "회원가입 성공"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 로그인 JWT (Access Token, Refresh Token)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# 로그아웃
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=LogoutSerializer,
        operation_summary="로그아웃",
        responses={200: "성공", 400: "토큰 유효하지 않음", 401: "인증 오류", 500: "서버 에러"},
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "로그아웃 성공"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 비밀번호 변경
class PasswordChangeView(APIView):
    permission_classes = [IsOwner]

    def get_objects(self, user_id):
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(self.request, user)
        return user

    @swagger_auto_schema(
        request_body=PasswordChangeSerializer,
        operation_summary="비밀번호 변경",
        responses={200: "성공",400: "인풋값 에러",401: "인증 오류",403: "권한 오류",404: "찾을 수 없음",500: "서버 에러"},
    )
    def put(self, request):
        user = self.get_objects(request.user.id)
        serializer = PasswordChangeSerializer(user, data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "비밀번호 변경이 완료되었습니다! 다시 로그인해주세요."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 비밀번호 찾기
class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=PasswordResetSerializer,
        operation_summary="비밀번호 찾기",
        responses={200: "성공", 400: "인풋값 에러", 500: "서버 에러"},
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "비밀번호 재설정 이메일을 발송했습니다. 확인부탁드립니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 비밀번호 재설정 토큰 확인
class PasswordTokenCheckView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="비밀번호 재설정 토큰 확인",
        responses={200: "성공", 401: "링크 유효하지 않음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request, uidb64, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({"message": "링크가 유효하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({"uidb64": uidb64, "token": token}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as identifier:
            return Response({"message": "링크가 유효하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)


# 비밀번호 재설정
class SetNewPasswordView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=SetNewPasswordSerializer,
        operation_summary="비밀번호 재설정",
        responses={200: "성공", 400: "인풋값 에러", 500: "서버 에러"},
    )
    def put(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "비밀번호 재설정 완료"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 회원정보 인증 토큰 발급
class ObtainUserTokenView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=TokenSerializer,
        operation_summary="인증 토큰 발급",
        responses={200: "성공", 400: "인풋값 에러", 401: "인증 오류", 500: "서버 에러"},
    )
    def post(self, request):
        serializer = TokenSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            user = authenticate(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsOwner]

    def confrim_token(self, token):
        authentication_instance = ConfirmTokenAuthentication()

        try:
            token_user = authentication_instance.authenticate_credentials(token)
            return token_user.id

        except AuthenticationFailed as e:
            raise AuthenticationFailed(str(e))

    def get_objects(self, user_id):
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(self.request, user)
        return user

    # 프로필
    @swagger_auto_schema(
        operation_summary="프로필",
        responses={200: "성공", 401: "인증 오류", 403: "권한 오류", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request):
        user = self.get_objects(request.user.id)
        serializer = ProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 회원정보 수정
    @swagger_auto_schema(
        request_body=UserSerializer,
        operation_summary="회원정보 수정",
        responses={200: "성공", 400: "인풋값 에러", 401: "인증 오류", 403: "권한 오류", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def put(self, request):
        token = request.GET.get("token", None)

        user_id = self.confrim_token(token)
        user = self.get_objects(user_id)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "회원정보 수정 성공"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 회원정보 삭제
    @swagger_auto_schema(
        operation_summary="회원정보 삭제",
        responses={200: "성공", 401: "인증 오류", 403: "권한 오류", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def delete(self, request):
        token = request.GET.get("token", None)

        user_id = self.confrim_token(token)
        user = self.get_objects(user_id)
        user.delete()
        return Response({"message": "회원 삭제 성공"}, status=status.HTTP_200_OK)


class AttendanceCheckView(APIView):
    permission_classes = [IsOwner]

    def get_objects(self, user_id):
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(self.request, user)
        return user

    # 출석 체크
    @swagger_auto_schema(
        operation_summary="출석 체크",
        responses={200: "성공", 400: "출석체크 업데이트 실패 및 이미 함", 401: "인증 오류", 403: "권한 오류", 500: "서버 에러"},
    )
    def post(self, request):
        try:
            user = self.get_objects(request.user.id)
            user.process_attendance_check()
            return Response({"message": "출석 체크를 완료했습니다."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
