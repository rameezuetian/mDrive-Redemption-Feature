from rest_framework.permissions import BasePermission

# class IsAdminUser(BasePermission):
#     """
#     Allows access only to staff/admin users.
#     """
#     def has_permission(self, request, view):
#         return bool(request.user and request.user.is_staff)
    
    
    
class IsSuperAdminUser(BasePermission):
    """
    Full admin access — reports, staff management, everything.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)
    

class IsStaffOrAdmin(BasePermission):
    """
    Staff or Super Admin — can manage products and offers.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
    