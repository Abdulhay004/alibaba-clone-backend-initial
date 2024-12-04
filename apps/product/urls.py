from django.urls import path
from .views import (CategoryListView, CategoryDetailView,
                    CategoryProductsView,ProductListPostView,
                    ProductsDetailDeletePatchPutView)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<uuid:id>/', CategoryDetailView.as_view(), name='category-detail'),
    # path('categories/<uuid:id>/products/', CategoryProductsView.as_view(), name='category-products'),
    path('', ProductListPostView.as_view(), name='product-list-and-post'),
    path('<uuid:id>/', ProductsDetailDeletePatchPutView.as_view(), name='product-detail-delete-patch-put')
]