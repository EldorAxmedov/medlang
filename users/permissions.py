from rest_framework import permissions


class IsAdminOrSelf(permissions.BasePermission):
    """Allow access if user is admin or the object belongs to the user."""

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == 'admin' or request.user.is_superuser:
            return True
        return getattr(obj, 'id', None) == getattr(request.user, 'id', None)
