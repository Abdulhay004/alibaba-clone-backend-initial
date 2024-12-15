from rest_framework.permissions import BasePermission

class IsSellerOrBuyer(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        groups = request.user.groups.values_list('name', flat=True)
        return 'seller' in groups or 'buyer' in groups