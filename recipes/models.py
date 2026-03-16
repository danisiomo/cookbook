# recipes/models.py

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Category(models.Model):
    """Категория рецептов"""
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL', unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug})


class Recipe(models.Model):
    """Рецепт"""
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    ingredients = models.TextField('Ингредиенты')
    instructions = models.TextField('Инструкция приготовления')
    cooking_time = models.PositiveIntegerField('Время приготовления (мин)', default=30)
    servings = models.PositiveIntegerField('Количество порций', default=1)

    # Связи
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Категория',
        related_name='recipes'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
    )

    # Метаданные
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('recipe_detail', kwargs={'pk': self.pk})


class RecipeImage(models.Model):
    """Изображения рецепта"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='images'
    )
    image = models.ImageField('Изображение', upload_to='recipes/')
    is_main = models.BooleanField('Главное', default=False)
    uploaded_at = models.DateTimeField('Загружено', auto_now_add=True)

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'
        ordering = ['-is_main', '-uploaded_at']

    def __str__(self):
        return f"Изображение для {self.recipe.title}"

    def save(self, *args, **kwargs):
        # Если это главное изображение, сбрасываем флаг у других
        if self.is_main:
            RecipeImage.objects.filter(recipe=self.recipe, is_main=True).update(is_main=False)
        else:
            # Если это первое изображение, делаем его главным
            if not RecipeImage.objects.filter(recipe=self.recipe).exists():
                self.is_main = True
        super().save(*args, **kwargs)