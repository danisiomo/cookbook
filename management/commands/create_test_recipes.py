from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from recipes.models import Recipe, Category


class Command(BaseCommand):
    help = 'Создает тестовые рецепты для проверки поиска'

    def handle(self, *args, **options):
        # Получаем или создаем пользователя
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@test.com'}
        )
        if created:
            user.set_password('testpass123')
            user.save()

        # Создаем тестовые рецепты
        test_recipes = [
            {
                'title': 'Тест22',
                'description': 'Тестовый рецепт с цифрами',
                'ingredients': 'Тест\nИнгредиент 1\nИнгредиент 2',
                'instructions': 'Смешать все\nПодавать'
            },
            {
                'title': 'Борщ',
                'description': 'Классический украинский борщ',
                'ingredients': 'Свекла\nКапуста\nМорковь\nКартофель',
                'instructions': 'Сварить бульон\nДобавить овощи'
            },
            {
                'title': 'Тестовый рецепт',
                'description': 'Просто тест',
                'ingredients': 'Ингредиенты для теста',
                'instructions': 'Инструкция для теста'
            }
        ]

        for recipe_data in test_recipes:
            recipe, created = Recipe.objects.get_or_create(
                title=recipe_data['title'],
                author=user,
                defaults={
                    'description': recipe_data['description'],
                    'ingredients': recipe_data['ingredients'],
                    'instructions': recipe_data['instructions'],
                    'cooking_time': 30,
                    'servings': 4
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан рецепт: {recipe.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Рецепт уже существует: {recipe.title}'))

        self.stdout.write(self.style.SUCCESS('Тестовые рецепты созданы!'))