from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Coupon
from .serializers import CouponSerializer
from .permissionns import IsSeller

class CustomPagination(PageNumberPagination):
    page_size = 10

class CouponView(generics.ListAPIView, generics.ListCreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]
    pagination_class = CustomPagination

    def get_queryset(self):
        return self.queryset.order_by('-valid_from')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class CouponUpdateAndDeleteView(generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]
    lookup_field = 'id'

    def perform_update(self, serializer):
        serializer.save()
