from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, PasswordField
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework import serializers, exceptions

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import update_last_login
from django.utils.translation import gettext_lazy as _
from django.db.models import F
from django.utils import timezone

from .models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = get_user_model().USERNAME_FIELD
    token_class = RefreshToken

    default_error_messages = {"no_active_account": _("이메일과 비밀번호를 확인해주세요. ")}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields["password"] = PasswordField()
    
    def validate(self, attrs):
        authenticate_kwargs = {self.username_field: attrs[self.username_field], "password": attrs["password"],}
        
        try:
            authenticate_kwargs["request"] = self.context["request"]
        except KeyError:
            pass
            
        self.user = authenticate(**authenticate_kwargs)
            
        try:
            email = attrs[self.username_field]
            self.status = User.objects.get(email=email).status
            lock_count = User.objects.get(email=email).lock_count

            #로그인 제한 횟수 counting
            if self.user == None:
                User.objects.filter(email=email).update(lock_count = F('lock_count')+1)

            #로그인 제한 횟수 counting이 5이면 회원 상태 S로 변경
            if lock_count == 5:
                User.objects.filter(email=email).update(status="S")             
                User.objects.filter(email=email).update(lock_time=timezone.now())
                
            #회원 상태 S이면 제한 시간 확인 후 N으로 변경
            now_today_time = timezone.now()
            
            if self.status == 'S':
                if now_today_time >= User.objects.get(email=email).lock_time + timezone.timedelta(minutes=5):
                    User.objects.filter(email=email).update(status="N")
                    User.objects.filter(email=email).update(lock_count= 0)
            
            #회원상태 W이면 로그인 시 비활성화 해제
            if self.status == 'W':
                User.objects.filter(email=email).update(status="N")
            
        except:
            pass
        
        #회원 상태 에러 발생
        if User.objects.filter(email=attrs[self.username_field]).exists():
            
            #회원 상태 aw이면 관리자 회원 탈퇴 에러
            if self.status == 'AW':
                raise serializers.ValidationError("관리자가 차단한 계정입니다.")
            
            #회원 상태 S이면 계정잠금 에러
            if self.status == 'S':
                raise serializers.ValidationError("계정이 잠금이 되었습니다. 잠시 후 다시 시도해주시길 바랍니다. ")
        
        #로그인 실패 에러
        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise exceptions.AuthenticationFailed(self.error_messages["no_active_account"],"no_active_account",)

        #로그인 토큰 발행
        refresh = self.get_token(self.user)

        attrs["refresh"] = str(refresh)
        attrs["access"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)
        
        return {"access":attrs["access"], "refresh":attrs["refresh"]}

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['nickname'] = user.nickname
        return token
