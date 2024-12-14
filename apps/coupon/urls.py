from django.urls import path
from .views import CouponView, CouponUpdateAndDeleteView, CouponApplyView

urlpatterns = [
    path('', CouponView.as_view(), name='coupon-list-and-create'),
    path('<uuid:id>/', CouponUpdateAndDeleteView.as_view(), name='coupon-update-and-delete'),
    path('apply/', CouponApplyView.as_view(), name='apply-coupon'),
]
