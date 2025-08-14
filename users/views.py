from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import auth, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

from users.models import User
from .forms import ProfileForm, UserLoginForm, UserRegistrationForm
from orders.models import Appointment
from django.utils import timezone

from users.telegram_login_widget import telegram_login_widget_redirect, bot_token
from django_telegram_login.authentication import verify_telegram_authentication
from django_telegram_login.errors import (
    NotTelegramDataError, 
    TelegramDataIsOutdatedError,
)


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    form_class = UserLoginForm
    success_url = reverse_lazy('main:index')

    


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация'
        context['telegram_redirect'] = telegram_login_widget_redirect
        return context
    
    def get_success_url(self):
        redirect_page = self.request.POST.get('next', None)
        if redirect_page and redirect_page != reverse('user:logout'):
            return redirect_page
        return reverse_lazy('main:index')
    
    def form_valid(self, form):
        # session_key = self.request.session.session_key
        user = form.get_user()

        if user:
            auth.login(self.request, user)
            # if session_key:
                # forgot_carts = Cart.objects.filter(user=user)
                # if forgot_carts.exists():
                    # forgot_carts.delete()
                # Cart.objects.filter(session_key=session_key).update(user=user)
            messages.success(self.request, f"{user.username}, Вы вошли в аккаунт!")

            return HttpResponseRedirect(self.get_success_url())
        

    def form_invalid(self, form):
        messages.error(self.request, "Неверный номер телефона или пароль")
        return super().form_invalid(form)    
    
        

class UserRegistrationView(CreateView):
    template_name = 'users/registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('users:profile')


    def telegram_login(self, request):
        try:
            result = verify_telegram_authentication(bot_token=bot_token, request_data=request.GET)
            
            # Генерируем уникальные значения
            telegram_id = result['id']
            username = result.get('username') or f"tg_{telegram_id}"
            phone_number = f"tg_{telegram_id}"
            
            # Пытаемся найти пользователя по telegram_id
            user = User.objects.filter(telegram_id=telegram_id).first()
            
            if user:
                # Обновляем существующего пользователя
                user.telegram_username = result.get('username')
                user.telegram_photo_url = result.get('photo_url')
                user.first_name = result.get('first_name', '')
                if not user.phone_number:
                    user.phone_number = phone_number
                if not user.username:
                    user.username = username
                user.save()
            else:
                # Создаем нового пользователя
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    email='',
                    first_name=result.get('first_name', ''),
                    telegram_username=result.get('username'),
                    telegram_photo_url=result.get('photo_url'),
                    phone_number=phone_number,
                    password='telegram_auth',  # Пароль не используется
                )
                user.set_unusable_password()  # Более корректный способ для OAuth
                user.save()
            
            auth.login(request, user)
            messages.success(request, f"Вы успешно вошли через Telegram!")
            return HttpResponseRedirect(self.success_url)
        
        except TelegramDataIsOutdatedError:
            messages.error(request, 'Данные аутентификации устарели (более 1 дня)')
            return HttpResponseRedirect(reverse('users:login'))
        
        except NotTelegramDataError:
            messages.error(request, 'Данные не связаны с Telegram!')
            return HttpResponseRedirect(reverse('users:login'))

    def get(self, request, *args, **kwargs):
        if 'hash' in request.GET:
            return self.telegram_login(request)
        return super().get(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        context['telegram_redirect'] = telegram_login_widget_redirect
        return context
    
    def form_valid(self, form):
        # session_key = self.request.session.session_key
        user = form.instance
        
        if user:
            form.save()
            auth.login(self.request, user)

        # if  session_key:
            # Cart.objects.filter(session_key=session_key).update(user=user)
            
        messages.success(self.request, f"{user.username}, Вы успешно зарегистрированы и вошли в аккаунт")
        return HttpResponseRedirect(self.success_url)
    


class UserProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'users/profile.html'
    form_class = ProfileForm
    success_url = reverse_lazy('users:profile')
    current_name = None
    current_username = None


    def get_object(self, queryset=None):
        self.current_name = self.request.user.first_name
        self.current_username = self.request.user.username
        return self.request.user
    
    def form_valid(self, form):
        new_name = form.cleaned_data.get('first_name')
        new_username = form.cleaned_data.get('username')
        if self.current_name != new_name:
            self.request.user.edit_name = False
            self.request.user.save()
        if self.current_username != new_username:
            self.request.user.edit_username = False
            self.request.user.save()
        messages.success(self.request, "Данные успешно обновлены")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Произошла ошибка')
        return super().form_invalid(form)    
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Личный кабинет'
        if self.request.user.is_authenticated:
            user_app = Appointment.objects.filter(user=self.request.user)
            today = timezone.now().date()
            context['current_app'] = user_app.filter(date__date=today).order_by('-date', 'time')
            context['past_app'] = user_app.filter(date__date__lt=today).order_by('-date', 'time')
            context['future_app'] = user_app.filter(date__date__gt=today).order_by('-date', 'time')

        # context['orders'] = Order.objects.filter(user=self.request.user).prefetch_related(
                # Prefetch(
                    # "orderitem_set",
                    # queryset=OrderItem.objects.select_related("product"),
                # )
            # ).order_by("-id")
        return context
    

@login_required
def logout(request):
    messages.success(request, f"{request.user.username}, Вы вышли из аккаунта")
    auth.logout(request)
    return redirect(reverse('main:index'))
