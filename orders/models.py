from django.conf import settings
from django.db import models
from main.models import Color, Product


class AvailableDate(models.Model):
    date = models.DateField(unique=True, verbose_name='Дата')
    class Meta:
        verbose_name = 'Дата'
        verbose_name_plural = 'Дата'
        unique_together = ('date',)
    
    def __str__(self):
        return str(self.date)



class AvailableTime(models.Model):
    date = models.ForeignKey(AvailableDate, on_delete=models.CASCADE, related_name='available_times', verbose_name='Дата')
    time = models.TimeField(verbose_name='Время')
    freely = models.BooleanField(verbose_name='Свободно? ', default=True)
    
    class Meta:
        verbose_name = 'Время'
        verbose_name_plural = 'Время'
        unique_together = ('date', 'time')
    
    def __str__(self):
        return str(self.time)



class Appointment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь',null=True, blank=True, related_name='appointment')
    name = models.CharField('Имя', max_length=100)
    phone = models.CharField('Телефон', max_length=20)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Услуга')
    colors = models.ManyToManyField(Color, verbose_name='Выбранные цвета', blank=True)
    date = models.ForeignKey(AvailableDate, on_delete=models.CASCADE, verbose_name='Дата')
    time = models.ForeignKey(AvailableTime, on_delete=models.CASCADE, verbose_name='Время')
    comment = models.TextField(verbose_name='Комментарий', blank=True)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        unique_together = ('date', 'time')
    
    def __str__(self):
        return f'Заказ #{self.id} от {self.name}'