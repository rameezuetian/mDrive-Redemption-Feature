from rest_framework.permissions import BasePermission


class isAdminUser(BasePermission):
    """
    Allow Access only to staff /admin users
    """
    def  has_permission(self, request, view):
        return bool(request.user   and request.user.is_staff)