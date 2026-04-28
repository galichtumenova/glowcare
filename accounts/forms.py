from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите username'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'example@mail.com'
        })
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Расскажите немного о себе',
            'rows': 5
        })
    )
    profile_image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-input'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите пароль'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Повторите пароль'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'bio', 'profile_image', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите пароль'
        })
    )


class ProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'profile-input',
            'placeholder': 'Введите имя пользователя'
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'profile-input',
            'placeholder': 'Введите email'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'bio', 'profile_image']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'profile-textarea',
                'placeholder': 'Напишите немного о себе...',
                'rows': 4
            }),
            'profile_image': forms.ClearableFileInput(attrs={
                'class': 'profile-file-input'
            })
        }