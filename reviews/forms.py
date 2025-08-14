from django import forms
from reviews.models import Reviews

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Reviews
        fields = ['comment', 'stars']
        widgets = {
            'stars': forms.HiddenInput(),  # Скрытое поле для хранения значения
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Оставьте ваш отзыв...'
            })
        }