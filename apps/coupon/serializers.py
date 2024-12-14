from rest_framework import serializers
from .models import Coupon

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'created_by', 'code', 'active', 'discount_type', 'discount_value', 'valid_from', 'valid_until']
