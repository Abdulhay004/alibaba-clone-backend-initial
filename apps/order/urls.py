from django.urls import path
from .views import OrderCheckoutView

urlpatterns = [
    path('checkout/', OrderCheckoutView.as_view(), name='order-checkout'),
]