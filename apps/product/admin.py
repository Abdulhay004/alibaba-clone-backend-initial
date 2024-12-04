from django.contrib import admin
from .models import Category, Product, Image, Size, Color


admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Image)
admin.site.register(Size)
admin.site.register(Color)