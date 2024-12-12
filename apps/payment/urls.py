from django.urls import path
from .views import PaymentInitiateView, PaymentConfirmView, PaymentCreateLinkView

urlpatterns = [
    path('<uuid:order_id>/initiate/', PaymentInitiateView.as_view(), name='payment-initiate'),
    path('<uuid:order_id>/confirm/', PaymentConfirmView.as_view(), name='payment-confirm'),
    path('<uuid:id>/create/link/', PaymentCreateLinkView.as_view(), name='payment_create_link'),
]
