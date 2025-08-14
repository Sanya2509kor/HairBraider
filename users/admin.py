from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # Укажите поля, которые вы хотите видеть в админке
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'email', 'username', 'image', 'count_comments')}),
        ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                   'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2'),
        }),
    )
    list_display = ('phone_number', 'first_name', 'is_staff')
    search_fields = ('phone_number', 'first_name')
    ordering = ('phone_number',)

admin.site.register(User, CustomUserAdmin)