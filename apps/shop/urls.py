from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    AddToCartView
)

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
]