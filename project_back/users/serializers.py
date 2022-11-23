from rest_framework import serializers
from django.contrib.auth.hashers import check_password

import re

from .models import User

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
        if not term_check or term_check == False :
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

class ProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('email', 'nickname', 'profile_image', 'point',)