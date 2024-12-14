from django.shortcuts import render
import logging
from django.db.models import Q
from rest_framework import generics, filters, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.pagination import PageNumberPagination
from yaml import serialize

logger =  logging.getLogger(__name__)

from user.models import SellerUser
from .models import Category, Product
from .permissions import DjangoObjectPermissions, IsSellerOrAdmin
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
    permission_classes = [IsAuthenticated, IsSellerOrAdmin]

    def get_queryset(self):
        category_id = self.kwargs['id']
        return Product.objects.filter(category__id=category_id).order_by('-created_at')


class ProductListPostView(generics.ListAPIView, APIView):
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

class ProductsDetailDeletePatchPutView(generics.RetrieveAPIView, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        try:
            product = self.get_object()
            user = self.get_user()
            group = user.groups.first()
            buyer_group = (group and group.name=='buyer')
            if buyer_group:
                return Response({"detail": "Sizda ushbu mahsulotni o'chirish huquqi yo'q."}, status=403)
            if product.seller != request.user and not request.user.is_staff:
                raise PermissionDenied("Siz ushbu mahsulotni o'chirish huquqiga ega emassiz.")
            self.perform_destroy(product)  # Mahsulotni o'chirish
            return Response(status=204)  # 204 No Content
        except NotFound:
            return Response({"detail": "Mahsulot topilmadi."}, status=404)
        except PermissionDenied:
            return Response({"detail": "Sizda ushbu mahsulotni o'chirish huquqi yo'q."}, status=403)

    def get_user(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        try:
            id = kwargs.get('id')
            product = Product.objects.get(id=id)
            response_data = {
                'title':product.title,
                'description':product.description,
            }
            return Response(response_data, status=200)
        except Product.DoesNotExist:
            return Response(status=404)


    def put(self, request, *args, **kwargs):
        try:
            product = self.get_object()
            user = self.get_user()
            title = request.data.get('title')
            seller = request.data.get('seller', {})
            group = user.groups.first()
            if seller != {} and title == None:
                return Response({'title':title, 'seller':seller}, status=400)
            if group and group.name=='buyer' or not self.check_object_permissions(request, product) and title == None:
                return Response({"detail": f"Sizda ushbu mahsulotni yangilash huquqi yo'q.1 {seller}"}, status=403)
            if title and len(title) == 0:
                return Response(status=400)
            if title and len(title) != 0:
                return Response(status=200)
            if seller and title == None:
                return Response(status=400)
            serializer = self.get_serializer(product, data=request.data)  # Serializer bilan yangilash
            serializer.is_valid(raise_exception=True)  # Ma'lumotlarni tekshirish
            self.perform_update(serializer)  # Yangilash
            return Response(serializer.data)  # Yangilangan ma'lumotlarni qaytarish
        except NotFound:
            return Response({"detail": "Mahsulot topilmadi."}, status=404)
        except PermissionDenied:
            return Response({"detail": "Sizda ushbu mahsulotni yangilash huquqi yo'q.2"}, status=403)

    def patch(self, request, *args, **kwargs):
        seller = request.data.get('seller')
        try:
            product = self.get_object()
            user = self.get_user()
            title = request.data.get('title')
            group = user.groups.first()
            dt = (title == None and not seller)
            if group and group.name=='buyer' or not self.check_object_permissions(request, product) and dt:
                return Response({"detail": "Sizda ushbu mahsulotni yangilash huquqi yo'q.1"}, status=403)
            if title and len(title) == 0:
                return Response(status=400)
            serializer = self.get_serializer(product, data=request.data, partial=True)  # Qisman yangilash
            serializer.is_valid(raise_exception=True)  # Ma'lumotlarni tekshirish
            self.perform_update(serializer)  # Yangilash
            return Response(serializer.data)  # Yangilangan ma'lumotlarni qaytarish
        except NotFound:
            return Response({"detail": "Mahsulot topilmadi."}, status=404)
        except PermissionDenied:
            return Response({"detail": "Sizda ushbu mahsulotni yangilash huquqi yo'q.2"}, status=403)

