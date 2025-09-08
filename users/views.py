from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import auth, messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

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

# Импортируйте декоратор
from .utils import check_recaptcha


class TelegramLoginView(View):
    """Отдельный view для обработки Telegram аутентификации"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        print("Telegram login request received:", request.GET)
        
        if 'hash' not in request.GET:
            print("No hash parameter found")
            return redirect('users:login')
        
        try:
            # Проверяем данные Telegram
            result = verify_telegram_authentication(
                bot_token=bot_token, 
                request_data=request.GET
            )
            print("Telegram authentication successful:", result)
            
            telegram_id = result['id']
            username = result.get('username') or f"tg_{telegram_id}"
            first_name = result.get('first_name', 'Пользователь')
            
            # Ищем пользователя по telegram_id
            user = User.objects.filter(telegram_id=telegram_id).first()
            
            if not user:
                # Ищем по username если telegram_id не найден
                user = User.objects.filter(username=username).first()
            
            if user:
                # Обновляем существующего пользователя
                print(f"Updating existing user: {user}")
                user.telegram_id = telegram_id
                user.telegram_username = result.get('username')
                user.telegram_photo_url = result.get('photo_url')
                user.first_name = first_name
                
                # Сохраняем только если номер начинается с tg_
                if not user.phone_number or user.phone_number.startswith('tg_'):
                    user.phone_number = f"tg_{telegram_id}"
                
                if not user.username or user.username.startswith('tg_'):
                    user.username = username
                
                user.save()
                print(f"User updated: {user}")
            else:
                # Создаем нового пользователя
                print("Creating new user")
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    telegram_username=result.get('username'),
                    telegram_photo_url=result.get('photo_url'),
                    phone_number=f"tg_{telegram_id}",
                )
                user.set_unusable_password()
                user.save()
                print(f"New user created: {user}")
            
            # Логиним пользователя
            auth.login(request, user)
            messages.success(request, f"Вы успешно вошли через Telegram!")
            print("User logged in successfully")
            return redirect('users:profile')
        
        except TelegramDataIsOutdatedError as e:
            print(f"Telegram data outdated: {e}")
            messages.error(request, 'Данные аутентификации устарели')
            return redirect('users:login')
        
        except NotTelegramDataError as e:
            print(f"Not Telegram data: {e}")
            messages.error(request, 'Ошибка аутентификации Telegram')
            return redirect('users:login')
        
        except Exception as e:
            print(f"Unexpected error: {e}")
            messages.error(request, f'Произошла ошибка: {str(e)}')
            return redirect('users:login')


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    form_class = UserLoginForm
    success_url = reverse_lazy('main:index')

    # Добавьте декоратор к dispatch методу
    @method_decorator(check_recaptcha)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

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
        # Проверяем капчу только для обычного входа
        if not self.request.recaptcha_is_valid:
            form.add_error(None, 'Ошибка проверки captcha. Подтвердите, что вы не робот.')
            return self.render_to_response(self.get_context_data(form=form))

        user = form.get_user()
        if user:
            auth.login(self.request, user)
            messages.success(self.request, f"{user.username}, Вы вошли в аккаунт!")
            return HttpResponseRedirect(self.get_success_url())
        
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Неверный номер телефона или пароль")
        return super().form_invalid(form)


class UserRegistrationView(CreateView):
    template_name = 'users/registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('users:profile')

    # Добавьте декоратор к dispatch методу
    @method_decorator(check_recaptcha)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        context['telegram_redirect'] = telegram_login_widget_redirect
        return context
    
    def form_valid(self, form):
        # Проверяем капчу
        if not self.request.recaptcha_is_valid:
            form.add_error(None, 'Ошибка проверки captcha. Подтвердите, что вы не робот.')
            return self.render_to_response(self.get_context_data(form=form))
        
        user = form.save()
        auth.login(self.request, user)
        messages.success(self.request, f"{user.username}, Вы успешно зарегистрированы и вошли в аккаунт")
        return HttpResponseRedirect(self.success_url)


class UserProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'users/profile.html'
    form_class = ProfileForm
    success_url = reverse_lazy('users:profile')
    current_name = None
    current_username = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['edit_name'] = self.request.user.edit_name
        kwargs['edit_username'] = self.request.user.edit_username
        return kwargs

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
            context['today'] = today  # Добавьте today в контекст
            context['current_app'] = user_app.filter(date__date=today).order_by('-date', 'time')[:5]
            context['past_app'] = user_app.filter(date__date__lt=today).order_by('-date', 'time')[:5]
            context['future_app'] = user_app.filter(date__date__gt=today).order_by('-date', 'time')[:5]
        return context


@login_required
def logout(request):
    messages.success(request, f"{request.user.username}, Вы вышли из аккаунта")
    auth.logout(request)
    return redirect(reverse('main:index'))