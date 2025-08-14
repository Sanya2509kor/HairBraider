from django.contrib import admin
from django.utils.html import format_html
from .models import Product, ProductImage, Color


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_preview')
    search_fields = ('name',)
    list_per_page = 20
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 80px; max-width: 80px; border-radius: 50%; border: 1px solid #ddd;"/>',
                obj.image.url
            )
        return "-"
    image_preview.short_description = "Изображение"


class ProductImageInline(admin.StackedInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'is_main')  # Убрали поле color


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    prepopulated_fields = {'slug': ('name',)}
    
    list_display = ('name', 'price', 'discount', 'display_colors', 'show_status')
    list_editable = ('discount', 'price')
    filter_horizontal = ('available_colors',)
    search_fields = ('name', 'description')
    list_filter = ('show', 'discount')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        ('Изображения и цены', {
            'fields': ('image', ('price', 'discount'))
        }),
        ('Настройки', {
            'fields': ('show', 'available_colors')
        }),
    )
    
    def display_colors(self, obj):
        colors = obj.available_colors.all()
        if not colors:
            return "-"
        return ", ".join([color.name for color in colors])
    display_colors.short_description = 'Доступные цвета'
    
    def show_status(self, obj):
        return obj.show
    show_status.short_description = 'Активно'
    show_status.boolean = True