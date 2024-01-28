from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from djoser.serializers import UserSerializer, UserCreateSerializer

from recipes.models import Recipe
from users.models import User, SubscribeUser


class CustomUserSerializer(UserSerializer):
    """
    Класс для сериализации пользователей.
    """
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        """
        Функция для получения значения поля is_subscribed.
        Проверяет, подписан ли текущий пользователь на данного пользователя.
        """
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return SubscribeUser.objects.filter(
            subscriber=user,
            target_user=obj.id
        ).exists()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        read_only_fields = (
            'is_subscribed',
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Класс для сериализации создания новых пользователей.
    """
    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class SubscribeFavoriteRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рецептов в избранном.
    """

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscribeSerializer(CustomUserSerializer):
    """
    Сериализатор для представления подписок.
    """
    recipes_count = SerializerMethodField()
    recipes = SubscribeFavoriteRecipeSerializer(
        many=True,
        source='get_user_recipes',
        read_only=True
    )

    def get_user_recipes(self, obj):
        """
        Функция для получения рецептов пользователя.
        """
        return Recipe.objects.filter(
            author=obj
        )

    def get_recipes_count(self, obj):
        """
        Функция для получения количества рецептов пользователя.
        """
        recipes = Recipe.objects.filter(
            author=obj.id
        )
        return recipes.count()

    class Meta(CustomUserSerializer.Meta):
        fields = (
            CustomUserSerializer.Meta.fields
            + ('recipes', 'recipes_count',)
        )

        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )
