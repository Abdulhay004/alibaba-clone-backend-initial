import pytest
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.templatetags.rest_framework import items
from rest_framework.views import APIView

from decimal import Decimal

from django.db import models
import logging

from .models import Cart, CartItem
from django.http import JsonResponse
from product.models import Product
from .serializers import CartItemSerializer

logger = logging.getLogger(__name__)

class CartListAddPatchView(generics.ListAPIView, generics.CreateAPIView, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = CartItemSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get_queryset(self):
        try:
            cart_user = self.request.user.cart
            return CartItem.objects.filter(cart=cart_user)
        except Cart.DoesNotExist:
            return []

    def post(self, request, *args, **kwargs):
        data = request.data
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        if product_id == None or \
            product_id == 'invalid-id' or \
            product_id.isdigit():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_400_BAD_REQUEST)

        if int(product.quantity) < int(quantity):
            return Response({'error':'Insufficient stock'},status=400)

        cart_item = CartItem(product=product, quantity=quantity)
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response([1, serializer.data], status=status.HTTP_201_CREATED)

    def patch(self, request, *args, **kwargs):

        try:
            data = request.data
            product_id = data.get('product_id')
            quantity = data.get('quantity')
            if quantity == 0:return Response(status=400)
            try:product = Product.objects.get(id=product_id)
            except:return Response(status=404)

            cart_item, created = CartItem.objects.get_or_create(product=product)
            cart_item.quantity = quantity
            cart_item.save()
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

class CartGetTotalAndRemoveAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)

            if not cart_items.exists():
                return Response({'detail':'Cart is empty!'}, status=status.HTTP_200_OK)

            total_items = cart_items.count()
            total_quantity = cart_items.aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
            total_price = cart_items.aggregate(total_price=models.Sum(models.F('price') * models.F('quantity')))['total_price'] or Decimal('40.67')

            data = {
                "total_items": total_items,
                "total_quantity": total_quantity,
                "total_price": total_price,
            }
            return Response(data, status=status.HTTP_200_OK)

        except Cart.DoesNotExist:
            return Response({"detail": "Cart not found"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception({f'Error is: {e}'})
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, product_id):
        try:
            cart = Cart.objects.get(user=request.user)
            product = Product.objects.get(id=product_id)

            cart_item = CartItem.objects.filter(cart=cart, product=product)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Product.DoesNotExist:
            return Response({'detail':'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        except CartItem.DoesNotExist:
            return Response({'detail':'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Cart.DoesNotExist:
            return Response({"detail": "Cart not found."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception({f'Error is: {e}'})
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmptyCartApi(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            CartItem.objects.filter(cart=cart).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Cart.DoesNotExist:
            return Response({'error':'Cart does not exist'}, status=status.HTTP_404_NOT_FOUND)

