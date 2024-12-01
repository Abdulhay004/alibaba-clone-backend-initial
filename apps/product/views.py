from django.shortcuts import render
from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import Category, Product
from .serializers import (CategorySerializer, ProductSerializer,)

class CustomPagination(PageNumberPagination):
    page_size = 10

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True).order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = self.queryset.prefetch_related('children')
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(Q(name__icontains=search))
        return queryset

class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

class CategoryProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        permissions = super().get_permissions()
        if self.request.method == 'GET' and \
                not self.request.user.groups.filter(name='seller').exists() and \
                not self.request.user.groups.filter(name='buyer').exists():
            self.permission_denied(self.request)  # 403 status kodi

        return permissions

    def get_queryset(self):
        category_id = self.kwargs['id']
        return Product.objects.filter(category__id=category_id)
