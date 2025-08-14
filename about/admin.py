from django.contrib import admin
from about.models import PortfolioImage, Portfolio

class PortfolioImageInline(admin.TabularInline):
    model = PortfolioImage
    extra = 1


@admin.register(Portfolio)
class ProductsAdmin(admin.ModelAdmin):

    inlines = [PortfolioImageInline]

    list_display = ['name' ]
    # list_editable = ['name']
    search_fields = ['name', 'description']
    list_filter = ['name']
    fields = [
        "name", 
        "description",
    ]

    ordering = ('-id',)
