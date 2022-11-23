from rest_framework import serializers, exceptions

from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.encoding import smart_bytes, force_str

import re

from .models import User
from .utils import Util
class UserSerializer(serializers.ModelSerializer):
    repassword= serializers.CharField(error_messages={'required':'비밀번호를 입력해주세요.', 'blank':'비밀번호를 입력해주세요.', 'write_only':True})    
    
    class Meta:
        model = User
        fields = ('email', 'nickname', 'password', 'repassword','profile_image', 'term_check',)
        extra_kwargs = {'email': {
                        'error_messages': {
                        'required': '이메일을 입력해주세요.',
                        'invalid': '알맞은 형식의 이메일을 입력해주세요.',
                        'blank':'이메일을 입력해주세요.',}},
                        
                        'nickname': {
                        'error_messages': {
                        'required': '닉네임을 입력해주세요.',
                        'blank':'닉네임을 입력해주세요',}},
                        
                        'password':{'write_only':True,
                        'error_messages': {
                        'required':'비밀번호를 입력해주세요.',
                        'blank':'비밀번호를 입력해주세요.',}},
                        } #extra_kwargs에 write_only하여 password만큼은 직렬화 시키지 않겠다.

    def validate(self, data):
        PASSWORD_VALIDATION = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,16}"
        PASSWORD_PATTERN = r"(.)\1+\1"
        NICKNAME_VALIDATION = r"^(?=.*[$@$!%*?&]){1,2}"
        
        nickname = data.get('nickname')
        password = data.get('password')
        repassword = data.get('repassword')
        term_check = data.get('term_check')
        
        #닉네임 유효성 검사
        if re.search(NICKNAME_VALIDATION, str(nickname)):
            raise serializers.ValidationError(detail={"nickname":"닉네임은 2자 이하 또는 특수문자를 포함할 수 없습니다."})
        
        if password:
            #비밀번호 일치
            if password != repassword:
                raise serializers.ValidationError(detail={"password":"비밀번호가 일치하지 않습니다."})
            
            #비밀번호 유효성 검사
            if not re.search(PASSWORD_VALIDATION, str(password)):
                raise serializers.ValidationError(detail={"password":"비밀번호는 8자 이상 16자이하의 영문 대/소문자, 숫자, 특수문자 조합이어야 합니다. "})
            
            #비밀번호 동일여부 검사
            if re.search(PASSWORD_PATTERN, str(password)):
                raise serializers.ValidationError(detail={"password":"비밀번호는 3자리 이상 동일한 영문,숫자,특수문자 사용 불가합니다. "})
        
        #이용약관 확인 검사
        if term_check == False:
            raise serializers.ValidationError(detail={"term_check":"약관동의를 확인해주세요."})
        
        return data
    
    #회원가입 create
    def create(self, validated_data):
        email = validated_data['email']
        nickname = validated_data['nickname']
        term_check = validated_data['term_check']
        user= User(
            nickname=nickname,
            email=email,
            term_check=term_check
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    #회원정보 수정 update
    def update(self, instance, validated_data):
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.save()
        return instance

class ChangePasswordSerializer(serializers.ModelSerializer):
    repassword= serializers.CharField(error_messages={'required':'비밀번호를 입력해주세요.', 'blank':'비밀번호를 입력해주세요.', 'write_only':True})    
    class Meta:
        model = User
        fields = ('password', 'repassword',)
        extra_kwargs = {'password':{'write_only':True,
                        'error_messages': {
                        'required':'비밀번호를 입력해주세요.',
                        'blank':'비밀번호를 입력해주세요.',}},}

    def validate(self, data):
        PASSWORD_VALIDATION = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,16}"
        PASSWORD_PATTERN = r"(.)\1+\1"
        
        current_password = self.context.get("request").user.password
        password = data.get('password')
        repassword = data.get('repassword')
        
        #현재 비밀번호와 바꿀 비밀번호 비교
        if check_password(password, current_password):
            raise serializers.ValidationError(detail={"password":"현재 사용중인 비밀번호와 동일한 비밀번호는 입력할 수 없습니다."})
        
        #비밀번호 일치
        if password != repassword:
            raise serializers.ValidationError(detail={"password":"비밀번호가 일치하지 않습니다."})
        
        #비밀번호 유효성 검사
        if not re.search(PASSWORD_VALIDATION, str(password)):
            raise serializers.ValidationError(detail={"password":"비밀번호는 8자 이상 16자이하의 영문 대/소문자, 숫자, 특수문자 조합이어야 합니다. "})
        
        #비밀번호 문자열 동일여부 검사
        if re.search(PASSWORD_PATTERN, str(password)):
            raise serializers.ValidationError(detail={"password":"비밀번호는 3자리 이상 동일한 영문/사용 사용 불가합니다. "})

        return data
    
    #비밀번호 변경 update
    def update(self, instance, validated_data):
        instance.password = validated_data.get('password', instance.password)
        instance.set_password(instance.password)
        instance.save()
        return instance
class PasswordResetSerializer(serializers.Serializer):
    email= serializers.EmailField(error_messages={'required':'이메일을 입력해주세요.', 'blank':'이메일을 입력해주세요.', 'invalid': '알맞은 형식의 이메일을 입력해주세요.'})    
    
    class Meta:
        fields = ('email',)
    
    def validate(self, attrs):
        email = attrs.get('email')
        
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email) 
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id)) 
            token = PasswordResetTokenGenerator().make_token(user) #토큰 생성
            current_site = get_current_site(self.context.get("request")).domain #현재 주소 
            relativeLink = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token}) #reverse로 password_reset_confrim으로 이동
            absurl = 'http://'+current_site + relativeLink #확인된 토큰 주소 생성
            email_body = '안녕하세요, \n 비밀번호 재설정 주소입니다.\n'+ absurl #이메일 내용
            message = {'email_body': email_body, 'to_email': user.email,'email_subject': '비밀번호 재설정'}
            Util.send_email(message)
            
            return super().validate(attrs)
        raise serializers.ValidationError(detail={"email":"잘못된 이메일입니다. 다시 입력해주세요."})

class SetNewPasswordSerializer(serializers.Serializer):
    password= serializers.CharField(error_messages={'required':'비밀번호를 입력해주세요.', 'blank':'비밀번호를 입력해주세요.', 'write_only':True}) 
    repassword= serializers.CharField(error_messages={'required':'비밀번호를 입력해주세요.', 'blank':'비밀번호를 입력해주세요.', 'write_only':True}) 
    token = serializers.CharField(max_length=100, write_only=True)
    uidb64 = serializers.CharField(max_length=100, write_only=True)
    class Meta:
        fields = ('repassword','password','token','uidb64',)
        
    def validate(self, attrs):
        try:
            PASSWORD_VALIDATION = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,16}"
            PASSWORD_PATTERN = r"(.)\1+\1"
            
            password = attrs.get('password')
            repassword = attrs.get('repassword')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            
            if PasswordResetTokenGenerator().check_token(user, token)==False:
                raise exceptions.AuthenticationFailed('링크가 일치하지 않습니다.', 401)
            
            #비밀번호 일치
            if password != repassword:
                raise serializers.ValidationError(detail={"password":"비밀번호가 일치하지 않습니다."})
            
            #비밀번호 유효성 검사
            if not re.search(PASSWORD_VALIDATION, str(password)):
                raise serializers.ValidationError(detail={"password":"비밀번호는 8자 이상 16자이하의 영문 대/소문자, 숫자, 특수문자 조합이어야 합니다. "})
            
            #비밀번호 문자열 동일여부 검사
            if re.search(PASSWORD_PATTERN, str(password)):
                raise serializers.ValidationError(detail={"password":"비밀번호는 3자리 이상 동일한 영문/사용 사용 불가합니다. "})
            
            user.set_password(password)
            user.save()
            
            return super().validate(attrs)
            
        except Exception as e:
            raise exceptions.AuthenticationFailed('링크가 일치하지 않습니다.', 401)






class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'nickname', 'profile_image', 'point',)
    