from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken


from django.contrib.auth.hashers import check_password

from .jwt_claim_serializer import CustomTokenObtainPairSerializer
from .serializers import UserSerializer, ChangePasswordSerializer
from .models import User

class UserView(APIView):
    
    #회원가입
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"가입성공"}, status=status.HTTP_201_CREATED )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST )
    
    #회원정보 수정
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
    def delete(self, request):
        user = User.objects.filter(id=request.user.id)
        if user:
            user.update(status="W")
            return Response({"message":"회원 비활성화 성공"}, status=status.HTTP_200_OK)
        return Response({"message":"접근 권한 없음"}, status=status.HTTP_403_FORBIDDEN)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    #비밀번호 인증
    def post(self, request):
        user = get_object_or_404(User, id=request.user.id)
        password = user.password
        if check_password(request.data["password"], password):
            return Response({"message":"인증이 완료되었습니다."}, status=status.HTTP_200_OK)        
        return Response({"message":"맞는 비밀번호를 적어주세요."}, status=status.HTTP_400_BAD_REQUEST)

    #비밀번호 변경
    def put(self, request):
        user = get_object_or_404(User, id=request.user.id)
        serializer = ChangePasswordSerializer(user, data=request.data, context={'request': request}) #request를 serializer로 넘김
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"비밀번호 변경이 완료되었습니다! 다시 로그인해주세요."} , status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    
    serializer_class = CustomTokenObtainPairSerializer
    
#미완성
# class KakaoLoginView(APIView):
#     # 소셜로그인 : 카카오 계정을 통해 로그인, 회원가입 진행
#     def post(self, request):
#         access_token = request.data["access_token"]
#         email = request.data["email"]
#         nickname = request.data["username"]

#         try:
#             user = User.objects.get(email=email)

#             if user and (user.password == None):
#                 return Response({"res_code": 1, 
#                                 "message": "서비스 이용을 위해 회원님의 정보가 필요합니다"}, 
#                                 status=status.HTTP_200_OK)
                
#             elif user and (user.password != None):
#                 refresh = RefreshToken.for_user(user)
#                 return Response({"res_code": 2, 
#                                 "message" : "로그인 성공",
#                                 "refresh": str(refresh), 
#                                 "access": str(refresh.access_token),
#                                 "username": nickname
#                                 }, status=status.HTTP_200_OK)
        
#         except User.DoesNotExist:
#             return Response({"res_code": 1, 
#                             "message": "서비스 이용을 위해 회원님의 정보가 필요합니다"}, 
#                             status=status.HTTP_200_OK)