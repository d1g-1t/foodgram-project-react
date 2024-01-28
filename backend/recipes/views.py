from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

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
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
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
        queryset = queryset.order_by('-pub_date')
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
        recipe = Recipe.objects.get(id=pk)
        user = request.user
        objects_exists = model.objects.filter(
            user=user,
            recipe=recipe
        ).exists()

        if request.method == 'POST':

            if objects_exists:
                return Response(
                    {'errors': 'Данный рецепт уже добавлен'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            model.objects.create(
                user=user,
                recipe=recipe
            )
            serializer = SubscribeFavoriteRecipeSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        else:

            if not objects_exists:
                return Response(
                    {'errors': 'Данного рецепта нет в списке'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            model.objects.filter(
                user=user,
                recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

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
        favorites = FavoriteRecipe.objects.filter(
            user=user
        )
        serializer = FavoriteSerializer(
            favorites,
            many=True
        )
        return Response(
            serializer.data, status=status.HTTP_200_OK
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
        )
        ingredients_result = []

        for ingredient in ingredients:
            name = ingredient.ingredient.name
            amount = ingredient.amount
            measurement_unit = ingredient.ingredient.measurement_unit

            flag = False
            for item in ingredients_result:
                if name == item[0]:
                    item[1] += amount
                    flag = True
                    break

            if not flag:
                ingredients_result.append(
                    [
                        name,
                        amount,
                        measurement_unit
                    ]
                )

        shopping_cart = 'Список покупок:\n'
        for item in ingredients_result:
            shopping_cart += (
                f'Наименование: {item[0]}, Количество: {item[1]} {item[2]}\n'
            )
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment;'
            'filename=shopping_cart.txt'
        )
        return response


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
