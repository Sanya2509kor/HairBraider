from django.urls import path
from reviews import views

app_name = 'reviews'

urlpatterns = [
    path('all/', views.ReviewsView.as_view(), name='reviews'),
    path('add-review/', views.CreateReviewView.as_view(), name='add_review'),
    path('my-reviews/', views.MyReviewsView.as_view(), name='my_reviews'),
    path('edit-review/<int:pk>', views.EditReviewView.as_view(), name='edit_review'),
]