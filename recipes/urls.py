from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('recipe/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/new/', views.recipe_create, name='recipe_create'),
    path('recipe/<int:pk>/edit/', views.recipe_edit, name='recipe_edit'),
    path('recipe/<int:pk>/delete/', views.recipe_delete, name='recipe_delete'),
    path('image/<int:pk>/delete/', views.image_delete, name='image_delete'),
    path('categories/', views.category_list, name='category_list'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('recipes/letter/<str:letter>/', views.recipe_list_by_first_letter, name='recipes_by_letter'),
    path('api/autocomplete/', views.recipe_autocomplete, name='recipe_autocomplete'),
    path('image/<int:pk>/delete/', views.image_delete, name='image_delete'),
    path('offline/', views.offline, name='offline'),
]