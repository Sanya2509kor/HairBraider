import random
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from users.models import User
from django.contrib.auth import get_user_model



class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Номер телефона",
        max_length=16,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )


class UserRegistrationForm(UserCreationForm):

    USERNAME_LIST = ['BraidsQueen', 'TwistyGirl', 'KnotsPro', 'BraidArtist']
    
    first_name = forms.CharField(
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ['first_name', 'phone_number', 'password1', 'password2']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("Пользователь с таким номером телефона уже существует.")
        return phone_number
    

    def save(self, commit=True):
        while True:
            username = f"{random.choice(self.USERNAME_LIST)}{random.randint(1, 999)}"
            if not User.objects.filter(username=username):
                self.instance.username = username
                break
        # Находим первое свободное имя из списка
        # for username in self.USERNAME_LIST:
        #     if not User.objects.filter(username=username).exists():
        #         self.instance.username = username
        #         break
        # else:
        #     # Если все имена заняты, генерируем случайное
        #     self.instance.username = f"user{User.objects.count() + 1}"
        
        return super().save(commit)


class ProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            "image",
            "first_name",
            "username",
            "phone_number",
            "email",
        )
    image = forms.ImageField(required=False)
    first_name = forms.CharField()
    username = forms.CharField()
    email = forms.CharField(required=False)

