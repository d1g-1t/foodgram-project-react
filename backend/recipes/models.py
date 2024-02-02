from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from colorfield.fields import ColorField

from users.models import User


class Ingredient(models.Model):
    """
    Модель ингредиента.

    Поля:
    - name: Название ингредиента (CharField)
    - measurement_unit: Единица измерения (CharField)
    """
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=10,
        blank=False,
        null=False,
        verbose_name='Единица измерения',
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Модель тега.

    Поля:
    - name: Тег (CharField)
    - color: Цвет тега (CharField)
    - slug: Страница тега (SlugField)
    """
    name = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        verbose_name='Название тега',
    )
    color = ColorField()
    slug = models.SlugField(
        max_length=200,
        blank=False,
        null=False,
        unique=True,
        verbose_name='Слаг тега',
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Модель рецепта.

    Поля:
    - author: Автор рецепта (ForeignKey)
    - ingredients: Ингредиенты (ManyToManyField)
    - tags: Тэги (ManyToManyField)
    - image: Фотографии блюда (ImageField)
    - name: Название рецепта (CharField)
    - text: Рецепт приготовления (TextField)
    - cooking_time: Время приготовления блюда (PositiveSmallIntegerField)
    - pub_date: Дата публикации (DateTimeField)
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
        through='RecipeIngredient',
    )
    tags = models.ManyToManyField(
        Tag,
        blank=False,
        verbose_name='Теги',
    )
    image = models.ImageField(
        blank=False,
        null=False,
        upload_to='recipesphoto/',
        verbose_name='Фотографии блюда',
    )
    name = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        verbose_name='Название рецепта',
    )
    text = models.TextField(
        blank=False,
        null=False,
        verbose_name='Рецепт приготовления',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(settings.COOKING_TIME_MIN),
            MaxValueValidator(settings.COOKING_TIME_MAX)
        ),
        blank=False,
        null=False,
        verbose_name='Время приготовления блюда (мин.)',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    def get_favorite_count(self):
        """
        Получение количества добавлений в избранные рецепты.
        """
        favorite_count = self.favorite_recipes.count()
        return favorite_count

    get_favorite_count.short_description = (
        'Количество добавлений в избранные рецепты.'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'name'),
                name='unique_author_recipe'
            ),
        )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """
    Модель количества ингредиента в рецепте.

    Поля:
    - ingredient: Ингредиент (ForeignKey)
    - recipe: Рецепт (ForeignKey)
    - amount: Количество (PositiveSmallIntegerField)
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name='Ингредиент в рецепте.',
    )
    amount = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(settings.AMOUNT_MIN),
            MaxValueValidator(settings.AMOUNT_MAX)
        ),
        verbose_name='Количество ингредиента в рецепте',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_ingredient_amount'
            ),
        )

    def __str__(self):
        return (
            f'Ингредиент: {self.ingredient}, '
            f'Количество: {self.amount} {self.ingredient.measurement_unit}'
        )


class FavoriteRecipe(models.Model):
    """
    Модель избранного рецепта.

    Поля:
    - user: Пользователь (ForeignKey)
    - recipe: Рецепт (ForeignKey)
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Рецепт',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_favorite'
            ),
        )

    def __str__(self):
        return (
            f'Рецепт "{self.recipe}" в избранном '
            f' у пользователя {self.user}.'
        )


class TagRecipe(models.Model):
    """
    Модель связи тега и рецепта.

    Поля:
    - tag: Тег (ForeignKey)
    - recipe: Рецепт (ForeignKey)
    """
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('tag', 'recipe'),
                name='unique_tag_recipe'
            ),
        )

    def __str__(self):
        return f'Тег "{self.tag}" применен к рецепту "{self.recipe}"'


class ShoppingCart(models.Model):
    """
    Модель списка покупок.

    Поля:
    - user: Пользователь (ForeignKey)
    - recipe: Рецепт (ForeignKey)
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['id', ]
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_shopping_cart'
            ),
        )

    def __str__(self):
        return (
            f'рецепт {self.recipe} в списке покупок у '
            f'пользователя {self.user}'
        )
