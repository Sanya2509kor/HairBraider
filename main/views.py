from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView, DetailView, ListView
from .models import Product
from users.models import User


class IndexView(ListView):
    template_name = 'main/index.html'
    model = 'Product'
    context_object_name = 'goods'
    paginate_by = 10
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'HairBraider'
        context['title_text'] = 'Наши услуги'
        context['text'] = 'Выберите стиль, который подчеркнет вашу индивидуальность'
        # context['goods'] = Product.objects.all()
        return context
    

    def get_queryset(self):

        goods = Product.objects.all()
        return goods
    
    

class ProductView(DetailView):
    template_name = 'main/product.html'
    slug_url_kwarg = 'product_slug'
    context_object_name = 'product'

    queryset = Product.objects.prefetch_related('related_products')  # Оптимизация


    def get_object(self, queryset=None):
        slug = self.kwargs.get(self.slug_url_kwarg)
        return get_object_or_404(Product, slug=slug) 
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        context['images'] = Product.objects.get(slug=self.kwargs.get(self.slug_url_kwarg)).images.all()
        context['first_name'] = self.request.GET.get('first_name')
        # context['related_products'] = self.object.related_products.all()[:6]  # Ограничиваем до 6 товаров
        return context
