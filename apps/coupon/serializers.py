from rest_framework import serializers
from .models import Coupon

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'created_by', 'code', 'active', 'discount_type', 'discount_value', 'valid_from', 'valid_until']

class ApplyCouponSerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(max_length=100)
    order_id = serializers.UUIDField()
    class Meta:
        model = Coupon
        fields = ['id', 'created_by', 'code', 'active', 'discount_type', 'discount_value', 'valid_from', 'valid_until', 'max_uses']