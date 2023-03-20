from rest_framework.permissions import BasePermission
from rest_framework.exceptions import APIException
from rest_framework import status


class GenericAPIException(APIException):
    def __init__(self, status_code, detail=None, code=None):
        self.status_code = status_code
        super().__init__(detail=detail, code=code)


class IsOwner(BasePermission):
    """
    사용자만 접근 가능 하고
    다른 사용자 또는 비회원은 접근 불가
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # User 객체에 접근했을 경우
        if obj.email == user.email:
            return True
        
        if user.is_authenticated:
            response = {"detail": "접근 권한 없습니다."}
            raise GenericAPIException(status_code=status.HTTP_403_FORBIDDEN, detail=response)
        
        if user.is_anonymous:
            response = {"detail": "인증이 필요합니다."}
            raise GenericAPIException(status_code=status.HTTP_401_UNAUTHORIZED, detail=response)