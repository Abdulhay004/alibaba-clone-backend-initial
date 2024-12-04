from rest_framework import permissions
from rest_framework.permissions import BasePermission
from .models import Product
from user.models import SellerUser

class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_perm('product.delete_product')

class IsBuyer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_perm('product.view_category')



class DjangoObjectPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser: #Admins are also allowed
            return True
        if isinstance(obj, Product):
            return obj.seller.user == request.user
        return False

class SellerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Foydalanuvchining seller bo'lishi va ruxsatga ega ekanligini tekshirish
        if request.user.is_authenticated:
            seller = getattr(request.user, 'seller', None)  # Foydalanuvchiga tegishli seller obyekti
            return seller is not None and seller.has_permission()  # has_permission() metodi sizning modelingizda aniqlanishi kerak
        return False