from django.shortcuts import get_object_or_404
from http import HTTPStatus
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from djoser.views import UserViewSet

from users.models import User, SubscribeUser
from users.permissions import CreateOrAuthenticatedUserPermission
from users.serializers import CustomUserSerializer, SubscribeSerializer


class CustomUserViewSet(UserViewSet):
    """
    Класс представления пользователей.

    Функции:
    - subscribe: Подписаться или отписаться от пользователя.
    - subscriptions: Получить список подписок пользователя.
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (CreateOrAuthenticatedUserPermission,)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        subscriber = request.user
        target_user = get_object_or_404(User, id=id)
        subscribe_existence = SubscribeUser.objects.filter(
            subscriber=subscriber.id,
            target_user=target_user.id
        ).exists()

        if request.method == 'POST':
            if subscribe_existence:
                return Response(
                    {'errors': 'Данная подписка уже существует'},
                    status=HTTPStatus.BAD_REQUEST
                )
            if subscriber == target_user:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=HTTPStatus.BAD_REQUEST
                )
            subscription = SubscribeUser(
                subscriber=subscriber,
                target_user=target_user
            )
            subscription.save()
            serializer = SubscribeSerializer(
                target_user,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=HTTPStatus.CREATED)

        if not subscribe_existence:
            return Response(
                {'errors': 'Данной подписки не существует'},
                status=HTTPStatus.BAD_REQUEST
            )
        subscription = SubscribeUser.objects.get(
            subscriber=subscriber,
            target_user=target_user
        )
        subscription.delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        subscriber = request.user
        queryset = User.objects.filter(
            subscribers__subscriber=subscriber
        )
        page = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
