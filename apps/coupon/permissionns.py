from rest_framework.permissions import BasePermission


class IsSeller(BasePermission):
    def has_permission(self, request, view):
        groups = request.user.groups.first()
        if groups == 'seller':
            return False
        else:
            return True