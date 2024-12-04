from django.shortcuts import render
import logging
from django.db.models import Q
from rest_framework import generics, filters, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from yaml import serialize

logger =  logging.getLogger(__name__)

from user.models import SellerUser
from .models import Category, Product
from .permissions import DjangoObjectPermissions
from .serializers import (CategorySerializer, ProductSerializer)

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

class ProductListView(generics.ListAPIView, APIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, DjangoObjectPermissions]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        group = user.groups.first()
        if group and group.name=='buyer' and self.request.method=='POST':
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = Product.objects.all()
        recommend_by_product_id = self.request.query_params.get('recommend_by_product_id')
        search = self.request.query_params.get('search')

        if recommend_by_product_id:
            try:
                product = Product.objects.get(pk=recommend_by_product_id)
                queryset = Product.objects.filter(category=product.category).exclude(pk=recommend_by_product_id).order_by('-category')
            except Product.DoesNotExist:
                queryset = Product.objects.none() # Handle case where product doesn't exist

        elif search:
            queryset = queryset.filter(title__icontains=search) | queryset.filter(description__icontains=search)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})

