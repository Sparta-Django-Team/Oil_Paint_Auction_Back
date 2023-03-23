# rest_framework
from rest_framework.exceptions import APIException
from rest_framework import status


class AttendanceCheckException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "출석체크 오류 발생"
    default_code = "attendance check error"
