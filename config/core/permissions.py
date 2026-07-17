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

    
class IsPartnerUser(BasePermission):
    """
    Allows access only to users with a linked Partner profile.
    """
    def has_permission(self , request , view):
        return bool(
            request.user and request.user.is_authenticated and hasattr(request.user , 'partner_profile')
        )
    
class IsStaffAdminOrPartner(BasePermission):
    """
    Allows Staff/Admin (full scan access) OR Partner (restricted to own offers, checked in the view).
    """
    def has_permission(self , request, view):
        return bool(
            request.user.is_staff or hasattr(request.user  , 'partner_profile')
        )
    
    
    
    