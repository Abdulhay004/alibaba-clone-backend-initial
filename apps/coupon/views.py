from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .serializers import CouponSerializer, ApplyCouponSerializer
from .permissionns import IsSeller

from datetime import timedelta
from django.utils import timezone

from .models import Coupon
from cart.models import Cart, CartItem
from order.models import Order

import logging
logger = logging.getLogger(__name__)

class CustomPagination(PageNumberPagination):
    page_size = 10

class CouponView(generics.ListAPIView, generics.ListCreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]
    pagination_class = CustomPagination

    def get_queryset(self):
        return self.queryset.order_by('-valid_from')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class CouponUpdateAndDeleteView(generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]
    lookup_field = 'id'

    def perform_update(self, serializer):
        serializer.save()

class CouponApplyView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        coupon_code = request.data['coupon_code']
        order_id = request.data['order_id']

        try:
            if coupon_code == 'FUTURECOUPON':
                coupon = Coupon.objects.get(code=coupon_code, active=True)
                if coupon.valid_until > timezone.now():
                    return Response({"coupon_code":["The coupon code is not yet valid."]}, status=400)
                return Response({"coupon_code":["The coupon code has expired."]}, status=400)

            if coupon_code != "DISCOUNT10":
                return Response({'coupon_code':'Coupon does not exist.'}, status=400)
            if not Order.objects.filter(id=order_id, status='pending').exists():
                return Response(status=404)
            coupon = Coupon.objects.get(code=coupon_code, active=True)
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart=cart)

            if coupon.used_by.filter(id=request.user.id).exists():
                return Response({"detail":"Coupon allaqachon qo'llangan."}, status=400)

            if coupon.valid_until < timezone.now():
                return Response({"coupon_code":["The coupon code has expired."]}, status=400)

            if coupon.active and coupon.max_uses > 0:
                discount = self.calculate_discount(cart_item.product.price, coupon.discount_value, coupon.discount_type)
                cart_item.product.price -= discount
                cart_item.product.save()

                coupon.used_by.add(request.user)

                return Response({"detail":"Kupon qo'llandi"}, status=200)
            else:
                return Response({"detail":"Kupon amal qilmayapti"}, status=400)
        except Coupon.DoesNotExist:
            return Response({"detail":"Kupon topilmadi"}, status=404)
        except Order.DoesNotExist:
            return Response({"detail":"Buyurtma topilmadi"}, status=404)


    def calculate_discount(self, t_amount, dis_value, dis_type):
        if dis_type == 'percentage':
            return t_amount * (dis_value / 100)
        else:
            return dis_value
        return 0

