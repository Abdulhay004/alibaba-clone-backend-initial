from django.db import models
import uuid

from user.models import SellerUser, User

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    patent = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=50)
    hex_value = models.CharField(max_length=7)

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True)
    colors = models.ManyToManyField(Color, related_name='products_color', blank=True)
    stock = models.PositiveIntegerField(default=0, null=True)
    sizes = models.ManyToManyField(Size, related_name='products_size', blank=True)
    quantity = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)


class Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"
