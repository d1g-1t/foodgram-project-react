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
        is_authenticated = request.user.is_authenticated
        is_safe_method = request.method in permissions.SAFE_METHODS
        return is_authenticated or is_safe_method
