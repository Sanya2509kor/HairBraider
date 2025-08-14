from datetime import timedelta
from django.db import models
from django.conf import settings  # Для ссылки на модель User

class Reviews(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Ссылка на модель пользователя
        on_delete=models.CASCADE,  # Удалять отзывы при удалении пользователя
        verbose_name='Пользователь',
        related_name='reviews'  # Позволит обращаться user.reviews.all()
    )
    comment = models.TextField(verbose_name='Комментарий', blank=True, null=True)
    stars = models.PositiveIntegerField(verbose_name='Звёзды', default=5)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        db_table = 'Отзывы'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']  # Сортировка по дате (новые сначала)

    def __str__(self):
        return f"Отзыв {self.id} от {self.user.username}"
    

    @property
    def expiry_date(self):
        return self.created_at + timedelta(days=1)