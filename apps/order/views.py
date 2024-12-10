from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from cart.models import Cart, CartItem
from .models import Order, OrderItem
from .serializers import OrderCreateSerializer, OrderSerializer
from decimal import Decimal
from django.db import transaction


class OrderCheckoutView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_user()
        group = user.groups.first()
        if group is None:
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            with transaction.atomic(): # Ensure atomicity of order creation
                cart = Cart.objects.get(user=request.user)
                if not cart.items.exists():
                    return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

                if Order.objects.filter(user=request.user, status='pending').exists():
                    return Response({"detail": "You have a pending order."}, status=status.HTTP_400_BAD_REQUEST)

                total_price = Decimal(0)
                order_items_data = []
                for item in cart.items.all():
                    order_items_data.append({
                        'product': item.product,
                        'quantity': item.quantity,
                        'price': item.product.price, #get price from product
                    })
                    total_price += item.product.price * item.quantity


                order_data = {**serializer.validated_data, 'user': request.user, 'total_price': total_price, 'order_items': order_items_data}
                order = OrderSerializer().create(order_data)

                # Clear cart after successful order creation
                cart.items.clear()

                return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        except Cart.DoesNotExist:
            return Response({"detail": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
