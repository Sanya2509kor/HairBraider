from django.urls import path
from about import views

app_name = 'about'

urlpatterns = [
    path('about/', views.AboutView.as_view(), name='about'),
    path('portfolio/', views.PortfolioView.as_view(), name='portfolio'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
]