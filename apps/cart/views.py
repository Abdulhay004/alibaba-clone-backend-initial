import json
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
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

