"""Inventory URLs + backward-compatible product/plan aliases."""
from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response

from .views import (
    InventoryBarcodeView,
    InventoryDetailView,
    InventoryListCreateView,
    InventoryLowStockView,
)


urlpatterns = [
    # Core inventory endpoints
    path('inventory', InventoryListCreateView.as_view(), name='inventory-list-create'),
    path('inventory/low-stock', InventoryLowStockView.as_view(), name='inventory-low-stock'),
    path('inventory/barcode/<str:barcode>', InventoryBarcodeView.as_view(), name='inventory-barcode'),
    path('inventory/<int:item_id>', InventoryDetailView.as_view(), name='inventory-detail'),

    # Alias: /products → inventory?catalogType=isp_category
    path('products', InventoryListCreateView.as_view(), name='products-list-create'),
    path('products/active', InventoryListCreateView.as_view(), name='products-active'),
    path('products/<int:item_id>', InventoryDetailView.as_view(), name='products-detail'),

    # Alias: /plans → inventory?catalogType=isp_plan
    path('plans', InventoryListCreateView.as_view(), name='plans-list-create'),
    path('plans/<int:item_id>', InventoryDetailView.as_view(), name='plans-detail'),
]
