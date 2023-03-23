# rest_framework
from rest_framework import serializers, exceptions

# django
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator

# python
import re


def password_validator(value):
    password_validation = (r"^(?=.*[a-z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,16}")

    if not re.search(password_validation, str(value)):
        raise serializers.ValidationError('비밀번호는 8자 이상 16자 이하의 영문 소문자, 숫자, 특수문자 조합이어야 합니다.')


def repassword_validator(password, repassword):
    if password != repassword:
        raise serializers.ValidationError(detail={"repassword": "비밀번호가 일치하지 않습니다."})


def current_password_validator(current_password, password):
    if check_password(password, current_password):
        raise serializers.ValidationError(detail={"password": "현재 사용중인 비밀번호와 동일한 비밀번호는 입력할 수 없습니다."})


def nickname_validator(value):
    nickname_validation = (r"^[A-Za-z가-힣0-9]{3,10}$")

    if not re.search(nickname_validation, str(value)):
        raise serializers.ValidationError('닉네임은 3자이상 10자 이하로 작성해야하며 특수문자는 포함할 수 없습니다.')


def term_check_validator(value):
    if value == False:
        raise serializers.ValidationError('약관동의를 확인해주세요.')


def check_token_validator(user, token):
    if PasswordResetTokenGenerator().check_token(user, token) == False:
        raise exceptions.AuthenticationFailed("토큰이 유효하지 않습니다.", 401)