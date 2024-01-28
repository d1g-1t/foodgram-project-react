from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import IngredientsViewSet, RecipeViewSet, TagViewSet
from users.views import CustomUserViewSet


app_name = 'api'

router = DefaultRouter()

"""
Описание маршрутов:
/auth/ - Маршрут для аутентификации и получения токена доступа
/users/ - Маршрут для операций с пользователями
/recipes/ - Маршрут для операций с рецептами
/tags/ - Маршрут для операций с тегами
/ingredients/ - Маршрут для операций с ингредиентами
"""

router.register('users', CustomUserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
]
