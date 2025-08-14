from django.contrib import admin
from .models import AvailableDate, AvailableTime, Appointment
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class AvailableTimeInline(admin.TabularInline):
    model = AvailableTime
    extra = 1


@admin.register(AvailableDate)
class AvailableDateAdmin(admin.ModelAdmin):
    inlines = [AvailableTimeInline]
    list_display = ('date', )
    


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'name', 'phone', 'created_at', 'display_colors')
    list_filter = ('date', 'created_at', 'name', 'phone')
    search_fields = ('name', 'phone')
    filter_horizontal = ('colors',)
    readonly_fields = ('created_at', 'display_colors')
    
    fields = [
        'user',
        'name',
        'phone',
        'date',
        'time',
        'product',
        'display_colors',
        'colors',
        'comment',
        'created_at',
    ]
    

    def display_colors(self, obj):
        colors = obj.colors.all()
        if not colors:
            return "-"
        
        color_displays = []
        for color in colors:
            if color.image:
                display = f'<img src="{color.image.url}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 50%;  border: 1px solid #ccc;" title="{color.name}">'
            else:
                display = f'<div style="width: 50px; height: 50px; background-color: #eee; border: 1px solid #ccc;" title="{color.name}"></div>'
            color_displays.append(display)
        
        return mark_safe('<div style="display: flex; gap: 5px;">' + ''.join(color_displays) + '</div>')
    display_colors.short_description = 'Цвета'