from django.urls import path
from orders import views


app_name = 'order'

urlpatterns = [
    path('appointment/', views.AppointmentView.as_view(), name='appointment'),
    path('ajax/load-times/', views.load_times, name='ajax_load_times'),
    path('list_orders/', views.ListOrdersView.as_view(), name='list_orders'),
    path('list_orders_today/', views.ListOrdersTodayView.as_view(), name='list_orders_today'),
    # path('success/', views.success_view, name='success_page'),
]