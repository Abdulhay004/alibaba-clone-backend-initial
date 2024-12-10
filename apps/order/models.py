from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from product.models import Product

import uuid

User = get_user_model()

PAYMENT_METHODS = [
    ('click', 'Click'),
    ('payme', 'Payme'),
    ('card', 'Card'),
    ('paypal', 'Paypal'),
]

ORDER_STATUSES = [
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('canceled', 'Canceled'),
    ('delivered', 'Delivered'),
    # Add other statuses as needed
]


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    country_region = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=100)
    state_province_region = models.CharField(max_length=100, blank=True, null=True)
    postal_zip_code = models.CharField(max_length=20)
    telephone_number = models.CharField(max_length=50, null=True)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    total_price = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUSES, default='pending')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.pk} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT) # Assuming Product model exists
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2) # Price at the time of order

    def __str__(self):
        return f"{self.quantity} x {self.product.title} in Order #{self.order.pk}"
