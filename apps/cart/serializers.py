from rest_framework import serializers
from .models import CartItem, Cart
from product.models import Product, User, Category

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    class Meta:
        fields = ['id', 'name', 'is_active', 'created_at', 'parent', 'children']

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    views = serializers.IntegerField(required=False)
    class Meta:
        model = Product
        fields = ['id', 'category', 'title', 'description', 'price', 'image', 'quantity', 'views']

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'email', 'gender']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    seller = SellerSerializer()

    class Meta:
        model = CartItem
        fields = ['product', 'seller', 'quantity', 'price']
