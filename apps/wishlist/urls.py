from django.urls import path
from .views import WishlistView, WishlistDetailAndDeleteView

urlpatterns = [
    path('', WishlistView.as_view(), name='wishlist'),
    path('<uuid:id>/', WishlistDetailAndDeleteView.as_view(), name='wishlist-detail-and-delete'),
]