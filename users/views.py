from venv import logger

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import auth, messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
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
            # self.request.user.edit_name = False
            self.request.user.save()
        if self.current_username != new_username:
            # self.request.user.edit_username = False
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


# для восстановления пароля
from .models import PasswordResetCallSession
from .services import SMSRUService
from .forms import PasswordResetRequestForm, PasswordResetConfirmForm
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib.auth import update_session_auth_hash
import json

# users/views.py - обновите метод post в PasswordResetRequestView

# users/views.py - исправленный метод post в PasswordResetRequestView

class PasswordResetRequestView(View):
    """Шаг 1: Запрос на восстановление пароля по звонку"""
    
    def get(self, request):
        form = PasswordResetRequestForm()
        return render(request, 'users/password_reset_request.html', {
            'form': form,
            'title': 'Восстановление пароля'
        })
    
    def post(self, request):
        form = PasswordResetRequestForm(request.POST)
        
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            user = form.cleaned_user
            
            # Вызываем API SMS.RU
            smsru = SMSRUService()
            result = smsru.create_call_auth(phone)
            
            if result['success']:
                # Удаляем старые сессии
                PasswordResetCallSession.objects.filter(
                    user=user,
                    status='pending'
                ).delete()
                
                # Создаем новую сессию
                session = PasswordResetCallSession.objects.create(
                    user=user,
                    phone=phone,
                    check_id=result['check_id'],
                    call_phone=result['call_phone'],
                    status='pending'
                )
                
                print(f"Session created: id={session.id}, check_id={session.check_id}")  # Для отладки
                
                return render(request, 'users/password_reset_wait_call.html', {
                    'call_phone': result['call_phone_pretty'],
                    'check_id': result['check_id'],
                    'session_id': session.id,  # Убедитесь, что это поле передается
                    'expires_in': 300
                })
            else:
                messages.error(request, result['error'])
                return render(request, 'users/password_reset_request.html', {'form': form})
        
        return render(request, 'users/password_reset_request.html', {'form': form})


# users/views.py - добавьте эту функцию после класса PasswordResetRequestView

def check_password_reset_status(request, session_id):
    """AJAX проверка статуса звонка для восстановления пароля"""
    try:
        session = PasswordResetCallSession.objects.get(id=session_id)
        
        print(f"DEBUG: Checking status for session {session_id}, check_id={session.check_id}, status={session.status}")
        
        if session.status == 'confirmed':
            return JsonResponse({
                'status': 'confirmed',
                'reset_token': session.reset_token
            })
        
        if session.is_expired():
            session.status = 'expired'
            session.save()
            return JsonResponse({
                'status': 'expired',
                'message': 'Время истекло. Попробуйте снова.'
            })
        
        # Проверяем статус через API
        smsru = SMSRUService()
        result = smsru.check_status(session.check_id)
        
        print(f"DEBUG: SMS.RU API result = {result}")
        
        if result['success'] and result['is_confirmed']:
            session.status = 'confirmed'
            session.save()
            print(f"DEBUG: Session {session_id} confirmed!")
            return JsonResponse({
                'status': 'confirmed',
                'reset_token': session.reset_token
            })
        elif result['success']:
            print(f"DEBUG: Still pending, status_code={result.get('status_code')}")
            return JsonResponse({
                'status': 'pending',
                'message': f"Ожидаем звонок... Статус: {result.get('status_text', 'pending')}"
            })
        else:
            print(f"DEBUG: API error - {result.get('error')}")
            return JsonResponse({
                'status': 'error',
                'message': result.get('error', 'Ошибка проверки')
            })
            
    except PasswordResetCallSession.DoesNotExist:
        print(f"DEBUG: Session {session_id} not found!")
        return JsonResponse({
            'status': 'error',
            'message': 'Сессия не найдена'
        })


class PasswordResetConfirmView(View):
    """Шаг 3: Установка нового пароля после подтверждения звонком"""
    
    def get(self, request, token):
        try:
            session = PasswordResetCallSession.objects.get(
                reset_token=token,
                status='confirmed'
            )
            
            if session.is_expired():
                messages.error(request, 'Время для сброса пароля истекло. Запросите восстановление заново.')
                return redirect('users:password_reset_request')
            
            form = PasswordResetConfirmForm()
            return render(request, 'users/password_reset_confirm.html', {
                'form': form,
                'token': token
            })
        except PasswordResetCallSession.DoesNotExist:
            messages.error(request, 'Неверная или устаревшая ссылка для сброса пароля')
            return redirect('users:password_reset_request')
    
    def post(self, request, token):
        try:
            session = PasswordResetCallSession.objects.get(
                reset_token=token,
                status='confirmed'
            )
            
            if session.is_expired():
                messages.error(request, 'Время для сброса пароля истекло')
                return redirect('users:password_reset_request')
            
            form = PasswordResetConfirmForm(request.POST)
            
            if form.is_valid():
                user = session.user
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                
                # Обновляем сессию, чтобы пользователь не вышел
                update_session_auth_hash(request, user)
                
                # Удаляем сессию восстановления
                session.delete()
                
                messages.success(request, 'Пароль успешно изменен! Теперь вы можете войти с новым паролем.')
                return redirect('users:login')
            else:
                return render(request, 'users/password_reset_confirm.html', {
                    'form': form,
                    'token': token
                })
                
        except PasswordResetCallSession.DoesNotExist:
            messages.error(request, 'Неверная или устаревшая ссылка для сброса пароля')
            return redirect('users:password_reset_request')


@csrf_exempt
@require_http_methods(["POST"])
def password_reset_webhook(request):
    """
    Webhook для получения уведомлений от SMS.RU
    URL: /user/password-reset-webhook/
    """
    try:
        data = json.loads(request.body)
        check_id = data.get('check_id')
        status = data.get('status')  # 401 - подтвержден
        
        if check_id and status == '401':
            session = PasswordResetCallSession.objects.filter(
                check_id=check_id,
                status='pending'
            ).first()
            
            if session:
                session.status = 'confirmed'
                session.save()
                return JsonResponse({'status': 'ok'})
        
        return JsonResponse({'status': 'ignored'})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)