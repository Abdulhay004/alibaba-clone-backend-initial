from django.urls import path
from .views import OrderCheckoutView, OrderListView, OrderDetailView

urlpatterns = [
    path('checkout/', OrderCheckoutView.as_view(), name='orders-checkout'),
    path('<uuid:pk>/', OrderDetailView.as_view(), name='orders-detail'),
    path('', OrderListView.as_view(), name='orders-list'),
    path('history/', OrderListView.as_view(), name='orders-history'),
]