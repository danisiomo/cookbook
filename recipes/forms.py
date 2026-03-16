# recipes/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Recipe, RecipeImage


class RegisterForm(UserCreationForm):
    """Форма регистрации"""
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Имя пользователя'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Пароль'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Подтверждение пароля'})


class LoginForm(AuthenticationForm):
    """Форма входа"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Имя пользователя'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Пароль'})


class RecipeForm(forms.ModelForm):
    """Форма для создания/редактирования рецепта"""

    class Meta:
        model = Recipe
        fields = ['title', 'description', 'ingredients', 'instructions', 'cooking_time', 'servings', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название рецепта'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Краткое описание', 'rows': 3}),
            'ingredients': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Ингредиенты (каждый на новой строке)', 'rows': 5}),
            'instructions': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Инструкция приготовления (каждый шаг на новой строке)',
                       'rows': 8}),
            'cooking_time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Время в минутах'}),
            'servings': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Количество порций'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }


class RecipeImageForm(forms.ModelForm):
    """Форма для загрузки изображений"""

    class Meta:
        model = RecipeImage
        fields = ['image', 'is_main']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }