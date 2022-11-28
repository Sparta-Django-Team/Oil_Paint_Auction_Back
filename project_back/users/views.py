from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser

from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import DjangoUnicodeDecodeError, force_str


from drf_yasg.utils import swagger_auto_schema

from .jwt_claim_serializer import CustomTokenObtainPairSerializer
from .serializers import (UserSerializer, ChangePasswordSerializer, 
                        ProfileSerializer, SetNewPasswordSerializer, PasswordResetSerializer, LogoutSerializer)
from .models import User


class UserView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser,]
    
    #개인 프로필
    @swagger_auto_schema(operation_summary="개인 프로필",  
                        responses={ 200 : '성공', 404 :'찾을 수 없음', 500:'서버 에러'}) 
    def get(self, request):
        user = get_object_or_404(User, id=request.user.id)
        serializer = ProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #회원가입
    @swagger_auto_schema(request_body=UserSerializer, 
                        operation_summary="회원가입",  
                        responses={ 201 : '성공', 400 : '인풋값 에러', 500:'서버 에러'})
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"회원가입 성공"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #회원정보 수정
    @swagger_auto_schema(request_body=UserSerializer, 
                        operation_summary="회원정보 수정", 
                        responses={ 200 : '성공',  400 :'인풋값 에러', 403:'접근 권한 에러', 404 : '찾을 수 없음', 500:'서버 에러'})
    
    def put(self, request):
        user = get_object_or_404(User, id=request.user.id)
        if user == request.user:
            serializer = UserSerializer(user, data=request.data, partial=True)#partial 부분 수정 가능
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"회원정보 수정 성공"} , status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"접근 권한 없음"}, status=status.HTTP_403_FORBIDDEN)

    #계정 비활성화
    @swagger_auto_schema(operation_summary="계정 비활성화",
                        responses={ 200 : '성공', 403:'접근 권한 에러', 500:'서버에러'})
    def delete(self, request):
        user = User.objects.filter(id=request.user.id)
        if user:
            user.update(status="W")
            return Response({"message":"회원 비활성화 성공"}, status=status.HTTP_200_OK)
        return Response({"message":"접근 권한 없음"}, status=status.HTTP_403_FORBIDDEN)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    #비밀번호 인증
    @swagger_auto_schema(request_body=ChangePasswordSerializer, 
                        operation_summary="비밀번호 인증", 
                        responses={ 200 : '성공', 400:'인풋값 에러', 404:'찾을 수 없음', 500:'서버 에러'})
    def post(self, request):
        user = get_object_or_404(User, id=request.user.id)
        password = user.password
        if check_password(request.data["password"], password):
            return Response({"message":"인증이 완료되었습니다."}, status=status.HTTP_200_OK)        
        return Response({"message":"맞는 비밀번호를 적어주세요."}, status=status.HTTP_400_BAD_REQUEST)

    #비밀번호 변경
    @swagger_auto_schema(request_body=ChangePasswordSerializer, 
                        operation_summary="비밀번호 변경", 
                        responses={ 200 : '성공', 400:'인풋값 에러', 404:'찾을 수 없음', 500:'서버 에러'})
    def put(self, request):
        user = get_object_or_404(User, id=request.user.id)
        serializer = ChangePasswordSerializer(user, data=request.data, context={'request': request}) #request를 serializer로 넘김
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"비밀번호 변경이 완료되었습니다! 다시 로그인해주세요."} , status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#비밀번호 찾기(이메일 전송)
class PasswordResetView(APIView):
    
    @swagger_auto_schema(request_body=PasswordResetSerializer, 
                        operation_summary="비밀번호 찾기", 
                        responses={ 200 : '성공', 400:'인풋값 에러', 500:'서버 에러'})
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            return Response({"message":"비밀번호 재설정 이메일을 발송했습니다. 확인부탁드립니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#비밀번호 재설정 토큰 확인
class PasswordTokenCheckView(APIView):
    
    @swagger_auto_schema(operation_summary="비밀번호 재설정 토큰 확인", 
                        responses={ 200 : '성공', 401:'링크 유효하지 않음', 404:'찾을 수 없음', 500:'서버 에러'})
    def get(self, request, uidb64, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({"message":"링크가 유효하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response({'uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)
            
        except DjangoUnicodeDecodeError as identifier:
            return Response({"message":"링크가 유효하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)

#비밀번호 재설정
class SetNewPasswordView(APIView):
    
    @swagger_auto_schema(request_body=SetNewPasswordSerializer, 
                        operation_summary="비밀번호 재설정",
                        responses={ 200 : '성공', 400:'인풋값 에러', 500:'서버 에러'})
    def put(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message":"비밀번호 재설정 완료"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#로그인 JWT
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

#로그아웃
class LogoutAPIview(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(request_body=LogoutSerializer, 
                        operation_summary="로그아웃",
                        responses={ 200 : '성공', 400:'토큰 유효하지 않음', 500:'서버 에러'})
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"로그아웃 성공"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
