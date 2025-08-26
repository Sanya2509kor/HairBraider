from django.urls import path
from users import views 
from users.utils import check_recaptcha


app_name = 'users'

urlpatterns = [
    path('login/', check_recaptcha(views.UserLoginView.as_view()), name='login'),
    path('registration/', check_recaptcha(views.UserRegistrationView.as_view()), name='registration'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('logout/', views.logout, name='logout'),

]