from io import BytesIO
import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError
import requests
from django.core.files import File


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Ник',
        max_length=150,
        unique=True,
        blank=True,
        null=True
    )
    image = models.ImageField(upload_to='users_images', blank=True, null=True, verbose_name='Аватар')
    # phone_number = models.CharField(max_length=20, blank=True, null=True, unique=False)
    phone_number = models.CharField(
        verbose_name='Номер телефона', 
        max_length=12, 
        unique=True,
        blank=True,
        null=True,
        error_messages={
            'unique': "Пользователь с таким номером уже существует!",
        }
    )

    first_name = models.CharField(verbose_name='Имя', max_length=150)
    email = models.EmailField(blank=True, null=True, default='')  # разрешаем пустое значение
    count_comments = models.PositiveSmallIntegerField(verbose_name='Колличество комментариев может оставить', default=1, blank=True, null=True)
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    telegram_username = models.CharField(max_length=32, blank=True, null=True)
    telegram_photo_url = models.URLField(blank=True, null=True)
    edit_name = models.BooleanField(verbose_name='Изменять имя?', default=False)
    edit_username = models.BooleanField(verbose_name='Изменять имя пользователя?', default=False)

    USERNAME_FIELD = 'phone_number'  # Указываем, что phone_number теперь используется как идентификатор
    REQUIRED_FIELDS = ['first_name', 'username']  # Поля, запрашиваемые при создании суперпользователя

    def __str__(self):
        return self.phone_number
    
    def clean(self):
        # Проверяем, что хотя бы одно из идентификационных полей заполнено
        if not self.phone_number and not self.telegram_id:
            raise ValidationError("Должен быть указан либо номер телефона, либо Telegram ID")


    class Meta:
        db_table = 'user'
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'


    def save_telegram_image(self):
        if self.telegram_photo_url and not self.image:
            try:
                response = requests.get(self.telegram_photo_url)
                response.raise_for_status()  # Проверка на ошибки
                
                # Получаем имя файла из URL
                image_name = os.path.basename(self.telegram_photo_url)
                
                # Создаем временный файл в памяти
                image_file = BytesIO(response.content)
                
                # Сохраняем в ImageField
                self.image.save(image_name, File(image_file), save=True)
                
                return True
            except Exception as e:
                print(f"Ошибка при загрузке изображения: {e}")
                return False
        return False
    
    def save(self, *args, **kwargs):
        # При сохранении модели автоматически сохраняем изображение
        self.save_telegram_image()
        super().save(*args, **kwargs)


