from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from http import HTTPStatus
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.db.models import Sum, F

from recipes.filters import RecipesFilter, IngredientsFilter
from recipes.models import (Ingredient,
                            FavoriteRecipe,
                            RecipeIngredient,
                            Recipe, Tag,
                            ShoppingCart)
from recipes.serializers import (RecipeSerializer,
                                 CreateRecipeSerializer,
                                 FavoriteSerializer,
                                 IngredientSerializer,
                                 TagSerializer)
from users.permissions import AuthorOrAdminCanEditPermission
from users.serializers import SubscribeFavoriteRecipeSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Класс представления для модели Recipe.
    """
    CONTENT_TYPE = 'text/plain'
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        AuthorOrAdminCanEditPermission,
    )
    filterset_class = RecipesFilter

    def get_queryset(self):
        """
        Возвращает отсортированный по дате публикации queryset рецептов.
        """
        queryset = super().get_queryset()
        return queryset

    def get_serializer_class(self):
        """
        Возвращает сериализатор в зависимости от метода запроса.
        """
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateRecipeSerializer

    def favorite_shopping_cart_creator(self, model, request, pk):
        """
        Создает или удаляет объект модели FavoriteRecipe или ShoppingCart
        в зависимости от метода запроса.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        objects_exists = model.objects.filter(
            user=user,
            recipe=recipe
        ).exists()

        if request.method == 'POST':

            if objects_exists:
                return Response(
                    {'errors': 'Данный рецепт уже добавлен'},
                    status=HTTPStatus.BAD_REQUEST
                )

            model.objects.create(
                user=user,
                recipe=recipe
            )
            serializer = SubscribeFavoriteRecipeSerializer(recipe)
            return Response(
                serializer.data,
                status=HTTPStatus.CREATED
            )

        else:

            if not objects_exists:
                return Response(
                    {'errors': 'Данного рецепта нет в списке'},
                    status=HTTPStatus.BAD_REQUEST
                )

            model.objects.filter(
                user=user,
                recipe=recipe
            ).delete()
            return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
    )
    def favorite(self, request, pk):
        """
        Добавляет или удаляет рецепт из избранного.
        """
        return self.favorite_shopping_cart_creator(
            FavoriteRecipe, request, pk
        )

    @action(detail=False, methods=('GET',))
    def favorites(self, request):
        """
        Возвращает список избранных рецептов пользователя.
        """
        user = request.user
        favorites = user.user_favorite_recipes.all()
        serializer = FavoriteSerializer(
            favorites,
            many=True
        )
        return Response(
            serializer.data, status=HTTPStatus.OK
        )

    @action(
        detail=True,
        methods=('POST', 'DELETE')
    )
    def shopping_cart(self, request, pk):
        """
        Добавляет или удаляет рецепт из списка покупок.
        """
        return self.favorite_shopping_cart_creator(
            ShoppingCart, request, pk
        )

    @action(
        detail=False,
        methods=('GET',)
    )
    def download_shopping_cart(self, request):
        """
        Скачивает список покупок в виде текстового файла.
        """
        user = request.user
        queryset = ShoppingCart.objects.filter(
            user=user
        )
        recipe_ids = queryset.values_list(
            'recipe_id', flat=True
        )
        ingredients = RecipeIngredient.objects.filter(
            recipe_id__in=recipe_ids
        ).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')
        ).annotate(total_amount=Sum('amount'))

        shopping_cart = 'Список покупок:\n'
        for item in ingredients:
            shopping_cart += (
                f'Наименование: {item["name"]}, '
                f'Количество: {item["total_amount"]} '
                f'{item["measurement_unit"]}\n'
            )
        response = HttpResponse(
            shopping_cart, content_type=self.CONTENT_TYPE
        )
        response['Content-Disposition'] = (
            f'attachment; filename={settings.SHOPPING_CART_FILENAME}'
        )

        return response

    class Meta:
        ordering = ['-pub_date']


class IngredientsViewSet(viewsets.ModelViewSet):
    """
    Класс представления для модели Ingredient.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filterset_class = IngredientsFilter
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    """
    Класс представления для модели Tag.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None
