from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Wishlist, Product
from .serializers import WishlistSerializer
from .permissions import IsSellerOrBuyer

class CustomPagination(PageNumberPagination):
    page_size = 10

class WishlistView(generics.ListCreateAPIView, generics.GenericAPIView):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated, IsSellerOrBuyer]
    pagination_class = CustomPagination

    def get_queryset(self):
        return self.queryset.filter(created_by=self.request.user).order_by('created_at')

    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')

        user_wishlist = Wishlist.objects.filter(created_by=request.user)

        if user_wishlist.filter(product_id=product_id).exists():
            return Response({"detail": "Product is already in the wishlist."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"product_id": ["Product not found."]}, status=status.HTTP_400_BAD_REQUEST)

        wishlist_item = Wishlist.objects.create(created_by=request.user, product=product)
        serializer = self.get_serializer(wishlist_item)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class WishlistDetailAndDeleteView(generics.RetrieveAPIView, generics.DestroyAPIView):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated, IsSellerOrBuyer]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(created_by=user)