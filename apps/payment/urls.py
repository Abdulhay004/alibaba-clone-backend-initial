from django.urls import path
from .views import PaymentInitiateView

urlpatterns = [
    path('<uuid:order_id>/initiate/', PaymentInitiateView.as_view(), name='payment-initiate'),
]
