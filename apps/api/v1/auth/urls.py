from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

urlpatterns = [
    # JWT token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Custom auth endpoints
    path('register/', views.RegisterView.as_view(), name='api-register'),
    path('login/', views.LoginView.as_view(), name='api-login'),
    path('logout/', views.LogoutView.as_view(), name='api-logout'),
    path('refresh/', views.RefreshTokenView.as_view(), name='api-refresh'),
    path('user/', views.current_user, name='api-current-user'),
    path('profile/', views.UserProfileView.as_view(), name='api-profile'),
    
    # Email verification endpoints
    path('verify-email/', views.verify_email, name='api-verify-email'),
    path('resend-otp/', views.resend_otp, name='api-resend-otp'),
    
    # Account management endpoints
    path('delete-account/', views.delete_account, name='api-delete-account'),
    path('cancel-deletion/', views.cancel_account_deletion, name='api-cancel-deletion'),
    
    # SSH Key management endpoints
    path('ssh/info/', views.ssh_key_info, name='api-ssh-key-info'),
    path('ssh/generate/', views.generate_ssh_key, name='api-ssh-key-generate'),
    path('ssh/delete/', views.delete_ssh_key, name='api-ssh-key-delete'),
    path('ssh/test/', views.test_ssh_connection, name='api-ssh-test-connection'),
]