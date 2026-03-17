import random  # Важно: весь модуль, не функция
import re
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Value, IntegerField, Case, When
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Recipe, Category, RecipeImage
from .forms import RegisterForm, LoginForm, RecipeForm, RecipeImageForm

import random  # Убедись, что эта строка есть в начале файла


def home(request):
    """Главная страница"""
    recipes = Recipe.objects.all().order_by('-created_at')[:6]
    categories = Category.objects.all()

    # Статистика
    total_recipes = Recipe.objects.count()
    total_categories = Category.objects.count()
    total_users = User.objects.count()

    return render(request, 'home.html', {
        'recipes': recipes,
        'categories': categories,
        'total_recipes': total_recipes,
        'total_categories': total_categories,
        'total_users': total_users,
    })

def offline(request):
    """Страница для офлайн режима"""
    return render(request, 'offline.html')

def recipe_list(request):
    """Страница со всеми рецептами с улучшенным поиском и пагинацией"""
    # Начинаем со всех рецептов
    recipes = Recipe.objects.all().order_by('-created_at')
    categories = Category.objects.all()

    # Получаем параметры
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category')

    # Применяем поиск если есть запрос
    if query:
        # Очищаем запрос от лишних пробелов
        cleaned_query = ' '.join(query.split())

        # Разбиваем на слова
        search_terms = cleaned_query.split()

        # Создаем Q объект для поиска
        q_objects = Q()

        for term in search_terms:
            if term:  # игнорируем пустые строки
                # Ищем во всех полях
                q_objects |= (
                        Q(title__icontains=term) |
                        Q(ingredients__icontains=term) |
                        Q(description__icontains=term) |
                        Q(instructions__icontains=term)
                )

        # Применяем фильтр
        if q_objects:
            recipes = recipes.filter(q_objects).distinct()

            # Для отладки - выведем в консоль
            print(f"Поиск: '{query}'")
            print(f"Термы: {search_terms}")
            print(f"Найдено рецептов: {recipes.count()}")

    # Применяем фильтр по категории
    if category_slug:
        recipes = recipes.filter(category__slug=category_slug)

    # Пагинация
    paginator = Paginator(recipes, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'recipes/recipe_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'current_category': category_slug
    })

def recipe_detail(request, pk):
    """Детальная страница рецепта"""
    recipe = get_object_or_404(Recipe, pk=pk)
    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe
    })


def category_list(request):
    """Список всех категорий"""
    categories = Category.objects.all()
    return render(request, 'recipes/category_list.html', {
        'categories': categories
    })


def register_view(request):
    """Регистрация пользователя"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    """Вход в систему"""
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вы успешно вошли в систему!')
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('home')


@login_required
def recipe_create(request):
    """Создание нового рецепта"""
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()

            # Обработка загруженных изображений
            images = request.FILES.getlist('images')
            for i, image in enumerate(images):
                RecipeImage.objects.create(
                    recipe=recipe,
                    image=image,
                    is_main=(i == 0)  # Первое изображение делаем главным
                )

            messages.success(request, 'Рецепт успешно создан!')
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm()

    return render(request, 'recipes/recipe_form.html', {
        'form': form,
        'title': 'Новый рецепт'
    })


@login_required
def recipe_edit(request, pk):
    """Редактирование рецепта"""
    recipe = get_object_or_404(Recipe, pk=pk)

    # Проверяем, что пользователь - автор рецепта
    if recipe.author != request.user and not request.user.is_staff:
        messages.error(request, 'Вы не можете редактировать этот рецепт')
        return redirect('recipe_detail', pk=pk)

    if request.method == 'POST':
        form = RecipeForm(request.POST, instance=recipe)
        if form.is_valid():
            form.save()

            # Обработка новых изображений
            images = request.FILES.getlist('images')

            # Если есть новые изображения и нет старых, первое делаем главным
            make_first_main = not recipe.images.exists()

            for i, image in enumerate(images):
                RecipeImage.objects.create(
                    recipe=recipe,
                    image=image,
                    is_main=(i == 0 and make_first_main)
                )

            messages.success(request, 'Рецепт успешно обновлен!')
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm(instance=recipe)

    return render(request, 'recipes/recipe_form.html', {
        'form': form,
        'recipe': recipe,
        'title': 'Редактирование рецепта'
    })


@login_required
def image_delete(request, pk):
    """Удаление изображения"""
    image = get_object_or_404(RecipeImage, pk=pk)
    recipe = image.recipe

    # Проверяем права
    if recipe.author != request.user and not request.user.is_staff:
        messages.error(request, 'Вы не можете удалить это изображение')
        return redirect('recipe_detail', pk=recipe.pk)

    if request.method == 'POST':
        # Если удаляем главное изображение, нужно сделать главным другое
        if image.is_main:
            # Находим другое изображение этого рецепта
            other_image = RecipeImage.objects.filter(recipe=recipe).exclude(pk=pk).first()
            if other_image:
                other_image.is_main = True
                other_image.save()

        # Запоминаем URL изображения для сообщения
        image_url = image.image.url
        image.delete()
        messages.success(request, 'Изображение успешно удалено')
    else:
        # Если GET запрос, показываем страницу подтверждения
        return render(request, 'recipes/image_confirm_delete.html', {'image': image, 'recipe': recipe})

    return redirect('recipe_detail', pk=recipe.pk)


def recipe_list_by_first_letter(request, letter):
    """Поиск рецептов по первой букве названия"""
    recipes = Recipe.objects.filter(title__istartswith=letter).order_by('title')
    categories = Category.objects.all()

    paginator = Paginator(recipes, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'recipes/recipe_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'current_letter': letter,
        'query': f'Начинаются с "{letter.upper()}"'
    })


def recipe_autocomplete(request):
    """API для автодополнения поиска"""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse([], safe=False)

    # Ищем похожие названия
    titles = Recipe.objects.filter(title__icontains=query).values_list('title', flat=True)[:5]

    # Ищем популярные ингредиенты (простой вариант - первые слова из ингредиентов)
    ingredients = []
    recipes_with_ingredients = Recipe.objects.filter(ingredients__icontains=query)[:3]
    for recipe in recipes_with_ingredients:
        for line in recipe.ingredients.split('\n'):
            if query.lower() in line.lower():
                # Берем первую строку с совпадением
                ingredients.append(line.strip()[:50])
                break

    results = list(titles) + ingredients
    return JsonResponse(results[:7], safe=False)  # максимум 7 подсказок


def recipe_detail(request, pk):
    """Детальная страница рецепта"""
    recipe = get_object_or_404(Recipe, pk=pk)

    # Похожие рецепты (из той же категории)
    similar_recipes = Recipe.objects.filter(category=recipe.category) \
                          .exclude(pk=recipe.pk)[:3]

    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe,
        'similar_recipes': similar_recipes
    })


@login_required
def recipe_delete(request, pk):
    """Удаление рецепта"""
    recipe = get_object_or_404(Recipe, pk=pk)

    # Проверяем права (автор или админ)
    if recipe.author != request.user and not request.user.is_staff:
        messages.error(request, 'Вы не можете удалить этот рецепт')
        return redirect('recipe_detail', pk=pk)

    if request.method == 'POST':
        title = recipe.title
        recipe.delete()
        messages.success(request, f'Рецепт "{title}" успешно удален')
        return redirect('recipe_list')

    # GET запрос - показываем страницу подтверждения
    return render(request, 'recipes/recipe_confirm_delete.html', {'recipe': recipe})