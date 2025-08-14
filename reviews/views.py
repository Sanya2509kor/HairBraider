from datetime import timedelta
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from reviews.models import Reviews
from reviews.forms import ReviewForm
from users.models import User
from django.utils import timezone


class ReviewsView(ListView):
    template_name = 'reviews/reviews.html'
    model = 'Reviews'
    context_object_name = 'reviews'
    paginate_by = 10
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Отзывы'
        if self.request.user.is_authenticated:
            context['user_has_comment'] = self.request.user.count_comments
        else:
            context['user_has_comment'] = False
        return context
    
    
    def get_queryset(self):
        objects = Reviews.objects.all()
        return objects


class CreateReviewView(LoginRequiredMixin, CreateView):
    model = Reviews
    form_class = ReviewForm
    success_url = reverse_lazy('reviews:my_reviews')
    template_name = 'reviews/make_review.html'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание отзыва'
        return context
    

    def form_valid(self, form):
        form.instance.user = self.request.user
        user = self.request.user
        user.count_comments -= 1
        user.save()
        return super().form_valid(form)


class MyReviewsView(ListView):
    template_name = 'reviews/my_reviews.html'
    context_object_name = 'my_reviews'
    model = 'Reviews'
    paginate_by = 10
    allow_empty = True


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Мои отзывы'
        context['current_date'] = timezone.now()

        return context
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Reviews.objects.none()  # Возвращаем пустой queryset для анонимных пользователей
        return Reviews.objects.filter(user=self.request.user)
    

class EditReviewView(UpdateView):
    model = Reviews
    form_class = ReviewForm
    success_url = reverse_lazy('reviews:my_reviews')
    template_name = 'reviews/edit_review.html'


    def dispatch(self, request, *args, **kwargs):
        review = self.get_object()

        time_passed = timezone.now() - review.created_at
        if time_passed > timedelta(hours=24):
            raise Http404
        

        if review.user != request.user:
            raise Http404
            
        return super().dispatch(request, *args, **kwargs)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование отзыва'
        context['comment'] = self.object.comment
        return context
    

    def form_valid(self, form):
        if form.instance.user != self.request.user:
            raise Http404
        return super().form_valid(form)
    

        
    