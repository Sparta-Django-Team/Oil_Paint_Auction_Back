# rest_framework
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

# django
from django.urls import path

# users
from users import views

urlpatterns = [
    # Auth
    path("auth/signup/", views.SignupView.as_view(), name="signup"),
    path("auth/token/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
    
    # Password
    path("auth/password/change/", views.PasswordChangeView.as_view(), name="password_change"),
    path("auth/password/reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path("auth/password/reset/<uidb64>/<token>/", views.PasswordTokenCheckView.as_view(), name="password_reset_confirm"),
    path("auth/password/reset/confirm/", views.SetNewPasswordView.as_view(), name="password_reset_confirm"),
    
    # Profile
    path("users/token/", views.ObtainUserTokenView.as_view(), name="user_token"),
    path("users/", views.UserProfileView.as_view(), name="user_profile"),
    
    # Attendance
    path("attendance/", views.AttendanceCheckView.as_view(), name="attendance_check"),
]
