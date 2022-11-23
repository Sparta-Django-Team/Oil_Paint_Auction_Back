from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path('', views.UserView.as_view(), name='user_view'),
    # path("kakao/", views.KakaoLoginView.as_view(), name="kakao"), #미완성
    path('api/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    #password
    path('changepassword/', views.ChangePasswordView.as_view(), name='change_password_view'),
    path('password-reset-email/', views.PasswordResetView.as_view(),name="password_reset_email"),
    path('password-reset/<uidb64>/<token>/',views.PasswordTokenCheckView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', views.SetNewPasswordView.as_view(), name='password_reset_complete'),
]