from datetime import timedelta
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

class ConfirmTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.get(key=key)
            
        except model.DoesNotExist:
            raise AuthenticationFailed("토큰 값이 없거나 잘못되었습니다.")

        if not token.user.is_active:
            raise AuthenticationFailed("사용자가 비활성화되었습니다.")

        utc_now = timezone.now()
        token_age = utc_now - token.created

        expiration_period = timedelta(hours=1)

        if token_age > expiration_period:
            token.delete()
            raise AuthenticationFailed("토큰이 만료되었습니다.")

        return token.user
