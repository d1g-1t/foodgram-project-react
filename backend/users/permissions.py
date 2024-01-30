from rest_framework import permissions


class AuthorOrAdminCanEditPermission(permissions.BasePermission):
    """
    Позволяет только автору или администратору редактировать объект.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.author or request.user.is_superuser


class CreateOrAuthenticatedUserPermission(permissions.BasePermission):
    """
    Позволяет создавать объекты или требует аутентификации пользователя.
    """
    def has_permission(self, request, view):
        if view.action == 'create':
            return True
        if view.action == 'me':
            return request.user.is_authenticated
        return request.method in permissions.SAFE_METHODS
