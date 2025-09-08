# users/urls.py
from django.urls import path
from .views import (
    UserLoginView, 
    UserRegistrationView, 
    UserProfileView, 
    logout,
    TelegramLoginView
)

app_name = 'users'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('registration/', UserRegistrationView.as_view(), name='registration'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('logout/', logout, name='logout'),
    path('telegram-login/', TelegramLoginView.as_view(), name='telegram_login'),
]