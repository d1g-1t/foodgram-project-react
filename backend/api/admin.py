from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.admin import UserAdmin

from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    RecipeIngredient,
    Recipe,
    ShoppingCart,
    Tag
)

from users.models import User


class CustomUserAdmin(UserAdmin):
    """
    Управление пользователями.
    """
    search_fields = (
        'email',
        'username'
    )


class RecipeIngredientInline(admin.TabularInline):
    """
    Инлайн для ингредиентов в рецепте.
    """
    model = RecipeIngredient
    extra = 1
    verbose_name_plural = 'Ингредиенты'
    fields = (
        'ingredient',
        'amount'
    )


class RecipeForm(forms.ModelForm):
    """
    Форма для рецептов.
    """
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=FilteredSelectMultiple(
            'теги',
            is_stacked=False
        ),
        required=False
    )

    class Meta:
        model = Recipe
        fields = '__all__'


class TagAdmin(admin.ModelAdmin):
    """
    Управление тегами.
    """
    list_display = (
        'name',
        'color',
        'slug',
    )


class RecipeAdmin(admin.ModelAdmin):
    """
    Управление рецептами.
    """
    inlines = [RecipeIngredientInline]
    list_display = (
        'name',
        'author',
        'display_tags'
    )
    list_filter = (
        'tags',
    )
    search_fields = (
        'name',
        'author__username',
        'author__email'
    )
    readonly_fields = ('get_favorite_count',)
    form = RecipeForm

    def display_tags(self, obj):
        return ', '.join(
            tag['name'] for tag in obj.tags.values()
        )
    display_tags.short_description = 'Теги'

    def get_favorite_count(self, obj):
        return obj.favorite_recipes.count()
    get_favorite_count.short_description = (
        'Количество добавлений рецепта в избранное.'
    )


class IngredientAdmin(admin.ModelAdmin):
    """
    Управление ингредиентами.
    """
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = (
        'measurement_unit',
    )
    search_fields = ('name',)


class FavoriteRecipeAdmin(admin.ModelAdmin):
    """
    Управление избранными рецептами.
    """
    list_display = (
        'user',
        'recipe'
    )
    list_filter = (
        'recipe__tags',
    )
    search_fields = (
        'user__username',
        'user__email',
        'recipe__name'
    )


class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Управление корзиной покупок.
    """
    list_display = (
        'recipe',
        'user'
    )
    list_filter = (
        'recipe__tags',
    )
    search_fields = (
        'recipe__name',
        'user__username',
        'user__email'
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
