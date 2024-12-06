from django.urls import path
from .views import CartListAddPatchView

urlpatterns = [
    path('', CartListAddPatchView.as_view(), name='cart-list'),
    path('add/', CartListAddPatchView.as_view(), name='cart-add'),
    path('update/', CartListAddPatchView.as_view(), name='cart-update'),
]