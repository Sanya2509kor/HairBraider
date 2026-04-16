# users/urls.py
from django.urls import path
from .views import (
    UserLoginView, 
    UserRegistrationView, 
    UserProfileView, 
    logout,
    TelegramLoginView,
    PasswordResetRequestView,
    check_password_reset_status,
    PasswordResetConfirmView,
    password_reset_webhook,
)

app_name = 'users'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('registration/', UserRegistrationView.as_view(), name='registration'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('logout/', logout, name='logout'),
    path('telegram-login/', TelegramLoginView.as_view(), name='telegram_login'),
    # Восстановление пароля по звонку
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/status/<int:session_id>/', check_password_reset_status, name='password_reset_status'),
    path('password-reset/confirm/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-webhook/', password_reset_webhook, name='password_reset_webhook'),
]