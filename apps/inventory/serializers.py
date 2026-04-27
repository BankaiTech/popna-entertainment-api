"""Serializers for Inventory."""
from rest_framework import serializers

from .models import Inventory


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'organization')


class InventoryListSerializer(serializers.ModelSerializer):
    """Lightweight representation for list views."""

    class Meta:
        model = Inventory
        fields = (
            'id', 'catalog_type', 'name', 'sku', 'category',
            'price', 'is_active', 'current_stock', 'stock_alert',
            'barcode', 'meta', 'created_at',
        )
