from rest_framework import serializers
from .models import Category, Product, SellerUser, Color, Size, Image

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'is_active', 'created_at', 'parent', 'children']

    def get_children(self, obj):
        children = obj.children.all()
        return CategorySerializer(children, many=True).data

class ImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['id', 'image']

    def get_image(self, obj):
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(obj.image.url)
        return None


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'hex_value']

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id','name', 'description']


class ProductSerializer(serializers.ModelSerializer):
    colors = ColorSerializer(many=True, required=False)
    sizes = SizeSerializer(many=True, required=False)
    images = ImageSerializer(many=True, required=False)
    price = serializers.FloatField()
    uploaded_images = serializers.ListField(child=serializers.ImageField(), required=False)
    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'images', 'description', 'category', 'quantity', 'colors', 'sizes', 'uploaded_images']
        read_only_fields = ['id', 'seller', 'colors', 'sizes']

    def create(self, validated_data):
        colors_data = validated_data.pop('colors', [])
        sizes_data = validated_data.pop('sizes', [])

        product = Product.objects.create(**validated_data)

        for color_data in colors_data:
            color_data['name'] = color_data['name'].lower()
            color_serializer = ColorSerializer(data=color_data)
            if color_serializer.is_valid():
                color_instance = color_serializer.save()
                product.colors.add(color_instance)  # Rangni mahsulotga qo'shish

        for size_data in sizes_data:
            size_data['name'] = size_data['name'].lower()
            size_serializer = SizeSerializer(data=size_data)
            if size_serializer.is_valid():
                size_instance = size_serializer.save()
                product.sizes.add(size_instance)  # O'lchamni mahsulotga qo'shish

        return product