from django.db import models
from user.models import User
import uuid

class Coupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    used_by = models.ManyToManyField(User, related_name='coupon_used', blank=True)
    code = models.CharField(max_length=20, unique=True)
    active = models.BooleanField(default=True)
    discount_type = models.CharField(max_length=10, choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    max_uses = models.IntegerField(null=True)

    def __str__(self):
        return self.code
