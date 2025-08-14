from django.contrib import admin
from reviews.models import Reviews

@admin.register(Reviews)
class UserAdmin(admin.ModelAdmin):
    
    list_display = ['user', 'comment', 'stars', 'created_at']
    search_fields = ['user', 'comment', 'stars', 'created_at']
    
