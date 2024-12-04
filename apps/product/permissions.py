from rest_framework import permissions
from rest_framework.permissions import BasePermission
from .models import Product
from user.models import SellerUser

class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_perm('product.add_product')

class IsBuyer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_perm('product.view_category')



class DjangoObjectPermissions(BasePermission):
    """
    Allows access only to objects that are related to the current user (seller)
    or to admins.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser: #Admins are also allowed
            return True
        if isinstance(obj, Product):
            return obj.seller.user == request.user
        return False