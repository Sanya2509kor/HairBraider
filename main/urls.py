from django.urls import path
from main import views

app_name = 'main'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<slug:product_slug>/', views.ProductView.as_view(), name='product'),
]
