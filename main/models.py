from django.db import models
from django.urls import reverse


class Color(models.Model):  # Изменил название на единственное число (более правильное соглашение)
    name = models.CharField(max_length=30, verbose_name='Название цвета')
    image = models.ImageField(upload_to='color_images/', verbose_name='Изображение цвета', blank=False, null=False, default=None)

    class Meta:
        db_table = 'main_color'
        verbose_name = 'Цвет'
        verbose_name_plural = 'Цвета'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Product(models.Model):


    name = models.CharField(max_length=150, verbose_name='Название', blank=False, null=False)
    slug = models.SlugField(max_length=200, unique=True, blank=False, null=False, verbose_name='URL')
    image = models.ImageField(upload_to='product_images', blank=False, null=False, verbose_name='Изображение')
    description = models.TextField(verbose_name='Текст', blank=True, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=0, verbose_name='Цена')
    discount = models.DecimalField(default=0.00, max_digits=4, decimal_places=2, verbose_name='Скидка в %')
    available_colors = models.ManyToManyField(Color, verbose_name='Доступные цвета', related_name='products', blank=True)
    show = models.BooleanField(verbose_name='Показать на сайте?', default=True)

    make_time = models.CharField(max_length=100, verbose_name='Время занятости', blank=True, null=True, default='30 мин')

    



    class Meta:
        db_table = 'Services'
        verbose_name = 'Услугу'
        verbose_name_plural = 'Услуги'
        ordering = ("name",)

    def __str__(self):
        return f'{self.name}'
    


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='Товар')
    image = models.ImageField(upload_to='product_images/', verbose_name='Изображение')
    is_main = models.BooleanField(default=False, verbose_name='Основное изображение')
    
    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товара'
        ordering = ['-is_main', 'id']
    
    def __str__(self):
        return f"Изображение {self.id} для {self.product.name}"




