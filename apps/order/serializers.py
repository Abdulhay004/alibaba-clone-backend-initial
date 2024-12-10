from rest_framework import serializers
from .models import Order, OrderItem
from product.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all()) # Adjust queryset if needed

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'payment_method', 'country_region', 'city', 'state_province_region',
                  'postal_zip_code', 'telephone_number', 'address_line_1', 'address_line_2',
                  'total_price', 'created_at', 'status', 'order_items']

    def create(self, validated_data):
        items_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order



class OrderCreateSerializer(serializers.ModelSerializer):
    payment_method = serializers.CharField(max_length=20, required=True)
    country_region = serializers.CharField(max_length=50, required=True)
    city = serializers.CharField(max_length=100, required=True)
    state_province_region = serializers.CharField(max_length=100, required=True)
    postal_zip_code = serializers.CharField(max_length=20, required=True)
    telephone_number = serializers.CharField(max_length=50, required=True)
    address_line_1 = serializers.CharField(max_length=255, required=True)
    address_line_2 = serializers.CharField(max_length=255, required=True)
    class Meta:
        model = Order
        fields = ['payment_method', 'country_region', 'city', 'state_province_region',
                  'postal_zip_code', 'telephone_number', 'address_line_1', 'address_line_2']
