from rest_framework.permissions import BasePermission

class IsValidUser(BasePermission):
    def has_permission(self, request, view):
        groups = request.user.groups.first()
        if groups == 'buyer' or groups == None:
            return False
        else:
            return True