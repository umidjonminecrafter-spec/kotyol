from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user is not None


class RequireRole(BasePermission):
    """
    Permission class that checks if the user has one of the allowed roles.
    Usage: permission_classes = [RequireRole]
    And set allowed_roles on the view.
    """
    def has_permission(self, request, view):
        if request.user is None:
            return False
        allowed_roles = getattr(view, 'allowed_roles', [])
        if not allowed_roles:
            return True
        if request.user.role == 'ADMIN':
            return True
        return request.user.role in allowed_roles


def require_roles(*roles):
    """Factory function to create a permission class with specific roles."""
    class RolePermission(BasePermission):
        def has_permission(self, request, view):
            if request.user is None:
                return False
            if request.user.role == 'ADMIN':
                return True
            return request.user.role in roles
    return RolePermission
