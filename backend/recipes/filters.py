from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientsFilter(FilterSet):
    """
    Фильтр для ингредиентов.
    """
    name = filters.CharFilter(
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipesFilter(FilterSet):
    """
    Фильтр для рецептов.
    """
    author = filters.NumberFilter(
        field_name='author'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        """
        Фильтрует рецепты, которые пользователь добавил в избранное.
        """
        if value and self.request.user.is_authenticated:
            return self.request.user.favorite_recipes.all()
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """
        Фильтрует рецепты, которые пользователь добавил в корзину покупок.
        """
        if value and self.request.user.is_authenticated:
            return self.request.user.user_shopping_cart.all()
        return queryset

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )
