from django.urls import path
from .views import (CategoryListView, CategoryDetailView,
                    CategoryProductsView,ProductListView)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<uuid:id>/', CategoryDetailView.as_view(), name='category-detail'),
    # path('categories/<uuid:id>/products/', CategoryProductsView.as_view(), name='category-products'),
    path('', ProductListView.as_view(), name='product-list'),
]