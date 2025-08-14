from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from main.models import Color
from .forms import AppointmentForm
from .models import AvailableTime, Appointment
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import CreateView, ListView
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin


class AppointmentView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'orders/appointment.html'
    success_url = reverse_lazy('main:index')

    def handle_no_permission(self):
        messages.warning(self.request, 'Для записи войдите в аккаунт или зарегистрируйтесь!!!')
        return super().handle_no_permission()

    def get_initial(self):
        initial = super().get_initial()
        product_id = self.request.GET.get('product_id')
        if product_id:
            initial['product'] = product_id  # Устанавливаем начальное значение
        
        if self.request.user.is_authenticated:
            initial['name'] = self.request.user.get_full_name()  # или user.first_name

        if hasattr(self.request.user, 'phone_number') and self.request.user.phone_number:
            initial['phone'] = self.request.user.phone_number

        colors = self.request.GET.getlist('colors', [])
        if colors:
            initial['colors'] = Color.objects.filter(id__in=colors)
        return initial
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Запись'
        context['colors'] = Color.objects.all()
        make_appoint = True
        if self.request.user.is_authenticated:
            if Appointment.objects.filter(user=self.request.user, date__date__gte=timezone.now().date()).count() >= 3 and not self.request.user.is_superuser:
                messages.warning(self.request, 'У вас уже есть 3 записи, вы пока не можете записаться!!!')
                make_appoint = False
        context['make_appoint'] = make_appoint
        return context


    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Получаем выбранный временной слот
                time_slot = form.cleaned_data['time']
                
                # Блокируем запись на время транзакции
                locked_time_slot = AvailableTime.objects.select_for_update().get(pk=time_slot.pk)
                
                # Проверяем доступность
                if not locked_time_slot.freely:
                    form.add_error('time', 'Это время уже занято')
                    return self.form_invalid(form)
                
                # Сохраняем запись
                self.object = form.save(commit=False)
                self.object.time = locked_time_slot
                self.object.save()
                form.save_m2m()

                # Если пользователь авторизован
                if self.request.user.is_authenticated:
                    # Связываем запись с пользователем
                    self.object.user = self.request.user

                    user = self.request.user
                    user.count_comments += 1
                    user.save()
                
                    # Получаем номер телефона из формы
                    # phone_number = form.cleaned_data.get('phone')
                
                    # # Если номер телефона был указан и отличается от текущего
                    # if (phone_number and 
                    #     hasattr(self.request.user, 'phone_number') and 
                    #     self.request.user.phone_number != phone_number):
                    
                    #     # Обновляем номер телефона пользователя
                    #     self.request.user.phone_number = phone_number
                    #     self.request.user.save()
                
                # Обновляем статус времени
                locked_time_slot.freely = False
                locked_time_slot.save()
                
                messages.success(self.request, 'Запись успешно создана!')
                return super().form_valid(form)
                
        except AvailableTime.DoesNotExist:
            form.add_error('time', 'Выбранное время не найдено')
            return self.form_invalid(form)
        except Exception as e:
            form.add_error(None, f'Произошла ошибка: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме')
        return super().form_invalid(form)
    

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    


def load_times(request):
    date_id = request.GET.get('date')
    times = AvailableTime.objects.filter(date_id=date_id, freely=True).order_by('time')
    return render(request, 'orders/times_dropdown_list_options.html', {'times': times})


class ListOrdersView(UserPassesTestMixin,  ListView):
    model = Appointment
    context_object_name = 'orders'
    template_name = 'orders/list_orders.html'
    paginate_by = 3  # Пагинация по 10 элементов
    raise_exception = True  # Возвращает 403 вместо 404
    # или
    permission_denied_message = "Доступ запрещен"  # Сообщение при отказе

    def test_func(self):
        """Проверка, что пользователь администратор"""
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        """Обработка случая, когда пользователь не админ"""
        raise Http404("Страница не найдена")  # Возвращаем 404



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        context['title'] = 'HairBraider'
        
        return context
    
    
    def get_queryset(self):
        # Базовый QuerySet с оптимизацией
        today = timezone.now().date()
        queryset = super().get_queryset().filter(date__date__gt=today)\
            .select_related('product', 'date', 'time')\
            .order_by('date__date', 'time__time')
        
        return queryset
    


class ListOrdersTodayView(UserPassesTestMixin, ListView):
    model = Appointment
    context_object_name = 'orders'
    template_name = 'orders/list_orders_today.html'
    paginate_by = 10  # Пагинация по 10 элементов
    raise_exception = True  # Возвращает 403 вместо 404

    permission_denied_message = "Доступ запрещен"  # Сообщение при отказе

    def test_func(self):
        """Проверка, что пользователь администратор"""
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        """Обработка случая, когда пользователь не админ"""
        raise Http404("Страница не найдена")  # Возвращаем 404



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        context['title'] = 'HairBraider'
        
        return context
    

    def get_queryset(self):
        # Базовый QuerySet с оптимизацией
        today = timezone.now().date()
        queryset = super().get_queryset().filter(date__date=today)\
            .select_related('product', 'date', 'time')\
            .order_by('time__time')
        
        return queryset