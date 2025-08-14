from django import forms
from main.models import Color
from .models import AvailableDate, AvailableTime, Appointment
from django.db.models import Exists, OuterRef
from django.utils import timezone
import pytz  # Импортируем pytz для работы с часовыми поясами


class AppointmentForm(forms.ModelForm):
    colors = forms.ModelMultipleChoiceField(
        queryset=Color.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False  # Если выбор цвета не обязателен
    )
    
    date = forms.ModelChoiceField(
        queryset=AvailableDate.objects.annotate(
            has_available_times=Exists(
                AvailableTime.objects.filter(
                    date=OuterRef('pk'),
                    freely=True
                )
            )
        ).filter(
            has_available_times=True,
            date__gte=timezone.localtime(timezone.now()).date()  # Используем локальное время
        ).order_by('date'),
        empty_label="---------",
        to_field_name="id"
    )

    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Можете написать свои пожелания',
            'class': 'form-control'
        }),
        required=False,
        label='Комментарий'
    )
    
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'name', 'phone', 'product', 'colors', 'comment']
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Получаем текущее время в Красноярске
        krasnoyarsk_tz = pytz.timezone('Asia/Krasnoyarsk')
        current_time = timezone.localtime(timezone.now(), krasnoyarsk_tz).time()
        
        # Фильтруем времена, которые еще не прошли сегодня
        self.fields['time'].queryset = AvailableTime.objects.none()
        
        if 'date' in self.data:
            try:
                date_id = int(self.data.get('date'))
                date = AvailableDate.objects.get(id=date_id)
                
                # Если выбран сегодняшний день, фильтруем по времени
                if date.date == timezone.localtime(timezone.now()).date():
                    self.fields['time'].queryset = AvailableTime.objects.filter(
                        date_id=date_id,
                        time__gte=current_time,
                        freely=True
                    )
                else:
                    self.fields['time'].queryset = AvailableTime.objects.filter(
                        date_id=date_id,
                        freely=True
                    )
            except (ValueError, TypeError, AvailableDate.DoesNotExist):
                pass
        elif self.instance.pk:
            self.fields['time'].queryset = self.instance.date.available_times.filter(
                freely=True
            )
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance