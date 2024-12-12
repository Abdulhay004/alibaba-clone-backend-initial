from django.urls import path
from .views import (PaymentInitiateView, PaymentConfirmView,
                    PaymentCreateLinkView, PaymentSuccessView,
                    PaymentCancelView)

urlpatterns = [
    path('<uuid:order_id>/initiate/', PaymentInitiateView.as_view(), name='payment-initiate'),
    path('<uuid:order_id>/confirm/', PaymentConfirmView.as_view(), name='payment-confirm'),
    path('<uuid:id>/create/link/', PaymentCreateLinkView.as_view(), name='payment_create_link'),
    path('<uuid:order_id>/success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('<uuid:order_id>/cancel/', PaymentCancelView.as_view(), name='payment_cancel')
]
