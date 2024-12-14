from django.urls import path
from .views import CouponView, CouponUpdateAndDeleteView

urlpatterns = [
    path('', CouponView.as_view(), name='coupon-list-and-create'),
    path('<uuid:id>/', CouponUpdateAndDeleteView.as_view(), name='coupon-update-and-delete'),
]
