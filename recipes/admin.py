from django.contrib import admin
from .models import Category, Recipe, RecipeImage


class RecipeImageInline(admin.TabularInline):
    model = RecipeImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'get_main_image')
    list_filter = ('category', 'author', 'created_at')
    search_fields = ('title', 'description', 'ingredients')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [RecipeImageInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'category', 'author')
        }),
        ('Ингредиенты и инструкция', {
            'fields': ('ingredients', 'instructions')
        }),
        ('Детали', {
            'fields': ('cooking_time', 'servings')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_main_image(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            return '✅'
        return '❌'

    get_main_image.short_description = 'Главное фото'


@admin.register(RecipeImage)
class RecipeImageAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'is_main', 'uploaded_at')
    list_filter = ('is_main', 'recipe')