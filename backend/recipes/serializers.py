from django.core.exceptions import PermissionDenied
from django.db import transaction

from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Ingredient, Recipe, RecipeIngredient,
                            FavoriteRecipe, ShoppingCart,
                            Tag, TagRecipe)
from users.serializers import CustomUserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredient.
    """

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
        read_only_fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeIngredientSerializer(IngredientSerializer):
    """
    Сериализатор для модели RecipeIngredient.
    """

    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class AddIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления ингредиентов в рецепт.
    """
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount'
        )


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Tag.
    """
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Recipe.
    """
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        """
        Возвращает True, если рецепт добавлен в избранное
        у текущего пользователя.
        """
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=user,
            recipe=obj,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """
        Возвращает True, если рецепт добавлен в корзину
        у текущего пользователя.
        """
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=user,
            recipe=obj
        ).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рецепта.
    """
    image = Base64ImageField()
    ingredients = AddIngredientSerializer(
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = CustomUserSerializer(
        read_only=True
    )
    cooking_time = serializers.IntegerField(
        min_value=1
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        """
        Проверяет валидность данных при создании
        или обновлении рецепта.
        """
        author = self.context['request'].user
        name = data.get('name')
        ingredients_list = []

        for index in range(len(data['ingredients'])):
            amount = data['ingredients'][index]['amount']

            if amount < 1:
                raise serializers.ValidationError(
                    {'amount':
                     'Значение должно быть больше 1.'}
                )

            if data['ingredients'][index]['id'] in ingredients_list:
                raise serializers.ValidationError(
                    {'error': 'Этот ингредиент уже был добавлен.'}
                )
            ingredients_list.append(data['ingredients'][index]['id'])

        if self.instance is not None:
            if self.instance.author != author:
                raise PermissionDenied
        else:
            if Recipe.objects.filter(
                author=author, name=name
            ).exists():
                raise serializers.ValidationError(
                    {'error':
                     'Этот рецепт уже был добавлен.'}
                )

        return data

    def recipe_create_or_update(self, ingredients, tags, recipe):
        """
        Создает или обновляет связанные модели RecipeIngredient и TagRecipe.
        """
        ingredient_amount = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(ingredient_amount)

        for tag in tags:
            TagRecipe.objects.create(recipe=recipe, tag=tag)

        recipe.tags.set(tags)

    @transaction.atomic
    def create(self, validated_data):
        """
        Создает новый рецепт.
        """
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(
            author=author,
            **validated_data
        )

        self.recipe_create_or_update(
            ingredients,
            tags,
            recipe
        )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Обновляет существующий рецепт.
        """
        instance.tags.clear()
        TagRecipe.objects.filter(
            recipe=instance
        ).delete()
        RecipeIngredient.objects.filter(
            recipe=instance
        ).delete()
        ingredients = validated_data.pop(
            'ingredients'
        )
        tags = validated_data.pop('tags')

        self.recipe_create_or_update(
            ingredients,
            tags,
            instance
        )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """
        Возвращает сериализованные данные рецепта.
        """
        return RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели FavoriteRecipe.
    """

    class Meta:
        model = FavoriteRecipe
        fields = (
            'id',
            'user',
            'recipe',
        )
