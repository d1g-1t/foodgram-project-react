from django.conf import settings
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
    amount = serializers.IntegerField(
        min_value=settings.AMOUNT_MIN,
        max_value=settings.AMOUNT_MAX,
        error_messages={
            'min_value': (
                f'Количество ингредиентов не должно быть '
                f'меньше {settings.AMOUNT_MIN}'
            ),
            'max_value': (
                f'Количество ингредиентов не должно быть '
                f'больше {settings.AMOUNT_MAX}'
            ),
        }
    )

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
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipeingredient_set',
        read_only=True,
    )
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
        return user.favorite_recipes.filter(
            id=obj.id
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
    cooking_time = serializers.IntegerField()

    def validate_cooking_time(self, value):
        if (value < settings.COOKING_TIME_MIN
                or value > settings.COOKING_TIME_MAX):
            raise serializers.ValidationError(
                'Время приготовления должно быть между '
                f'{settings.COOKING_TIME_MIN} и {settings.COOKING_TIME_MAX} '
                'минутами'
            )
        return value

    def recipe_create_or_update(self, ingredients, tags, recipe):
        """
        Создает или обновляет рецепт.
        """
        ingredient_objects = []
        for ingredient in ingredients:
            ingredient_object = RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
            ingredient_objects.append(ingredient_object)
        RecipeIngredient.objects.bulk_create(ingredient_objects)

        tag_objects = []
        for tag in tags:
            tag_object = TagRecipe(
                recipe=recipe,
                tag=tag
            )
            tag_objects.append(tag_object)
        TagRecipe.objects.bulk_create(tag_objects)

        recipe.tags.set(tags)

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
        ingredients_ids = [
            ingredient['id']
            for ingredient
            in data['ingredients']
        ]

        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError(
                {'error': 'Ингредиенты не должны повторяться.'}
            )

        if self.instance is None and Recipe.objects.filter(
            author=author,
            name=name
        ).exists():
            raise serializers.ValidationError(
                {'error': 'Этот рецепт уже был добавлен.'}
            )
        for index, ingredient in enumerate(data['ingredients']):
            if 'amount' not in ingredient:
                error_msg = (
                    f'Не указано количество для ингредиента {index}.'
                )
                raise serializers.ValidationError({'error': error_msg})

        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Обновляет существующий рецепт.
        """
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        RecipeIngredient.objects.filter(recipe=instance).delete()
        TagRecipe.objects.filter(recipe=instance).delete()

        for ingredient in ingredients:
            RecipeIngredient.objects.update_or_create(
                recipe=instance,
                ingredient_id=ingredient['id'],
                defaults={'amount': ingredient['amount']}
            )

        for tag in tags:
            TagRecipe.objects.update_or_create(
                recipe=instance,
                tag=tag
            )

        instance.tags.set(tags)
        return super().update(instance, validated_data)

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


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ShoppingCart.
    """
    recipe = RecipeSerializer(read_only=True)

    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'user',
            'recipe',
        )
