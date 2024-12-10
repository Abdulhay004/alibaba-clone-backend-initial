from django.urls import path
from .views import OrderCheckoutView, OrderDetailView

urlpatterns = [
    path('checkout/', OrderCheckoutView.as_view(), name='order-checkout'),
    path('<uuid:pk>/', OrderDetailView.as_view(), name='order-detail')
]