from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

from users.validators import username_validator


class User(AbstractUser):
    """
    Модель пользователя.

    Поля:
    - email: Email пользователя (EmailField)
    - username: Имя пользователя (CharField)
    - first_name: Имя пользователя (CharField)
    - last_name: Фамилия пользователя (CharField)
    """

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name'
    ]
    email = models.EmailField(
        max_length=254,
        blank=False,
        null=False,
        unique=True,
        verbose_name='Email пользователя',
    )
    username = models.CharField(
        max_length=150,
        validators=[username_validator, ],
        blank=False,
        null=False,
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name='Имя пользователя',
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name='Фамилия пользователя',
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_user',
            )
        ]

    def __str__(self):
        return self.username


class SubscribeUser(models.Model):
    """
    Модель подписки на пользователя.

    Поля:
    - subscriber: Пользователь, который подписывается (ForeignKey)
    - target_user: Пользователь, на которого подписываются (ForeignKey)
    """
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'subscriber',
                    'target_user'
                ],
                name='unique_user_subscribe'
            )
        ]

    def __str__(self):
        return (
            f'Пользователь {self.subscriber} '
            f'подписан на {self.target_user}'
        )
