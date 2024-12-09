from django.urls import path
from .views import CartListAddPatchView, CartGetTotalAndRemoveAPI, EmptyCartApi

urlpatterns = [
    path('', CartListAddPatchView.as_view(), name='cart-list'),
    path('add/', CartListAddPatchView.as_view(), name='cart-add'),
    path('update/', CartListAddPatchView.as_view(), name='cart-update'),
    path('total/', CartGetTotalAndRemoveAPI.as_view(), name='cart-total'),
    path('remove/<uuid:product_id>/', CartGetTotalAndRemoveAPI.as_view(), name='cart-remove'),
    path('empty/', EmptyCartApi.as_view(), name='cart-empty'),
]