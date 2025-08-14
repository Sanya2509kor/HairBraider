from django.urls import path
from main import views

app_name = 'main'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    # path('about/', views.AboutView.as_view(), name='about'),
    # path('reviews/', views.ReviewsView.as_view(), name='reviews'),
    # path('about/', views.IndexView.as_view, name='about'),
    path('<slug:product_slug>/', views.ProductView.as_view(), name='product'),
]
