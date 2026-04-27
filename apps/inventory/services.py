"""Business logic for Inventory."""
import logging

from django.db import transaction

from .models import Inventory

logger = logging.getLogger(__name__)


class InventoryService:

    @staticmethod
    def list_items(organization, filters=None):
        qs = Inventory.objects.filter(organization=organization)

        if not filters:
            return qs

        if filters.get('catalogType'):
            qs = qs.filter(catalog_type=filters['catalogType'])
        if filters.get('category'):
            qs = qs.filter(category__icontains=filters['category'])
        if filters.get('isActive') is not None:
            is_active = str(filters['isActive']).lower() == 'true'
            qs = qs.filter(is_active=is_active)
        if filters.get('search'):
            from django.db.models import Q
            term = filters['search']
            qs = qs.filter(Q(name__icontains=term) | Q(sku__icontains=term))

        # meta filter: provider (for isp_plan)
        if filters.get('provider'):
            qs = qs.filter(meta__provider=filters['provider'])

        return qs

    @staticmethod
    def low_stock_items(organization):
        """Items where current_stock <= stock_alert or current_stock <= reorder_level."""
        from django.db.models import F, Q
        return Inventory.objects.filter(
            organization=organization,
            catalog_type='product',
            is_active=True,
        ).filter(
            Q(stock_alert__isnull=False, current_stock__lte=F('stock_alert'))
            | Q(reorder_level__isnull=False, current_stock__lte=F('reorder_level'))
        )

    @staticmethod
    def get_by_barcode(barcode, organization):
        return Inventory.objects.get(barcode=barcode, organization=organization)

    @staticmethod
    def get_item(item_id, organization):
        return Inventory.objects.get(pk=item_id, organization=organization)

    @staticmethod
    def create_item(validated_data, organization):
        with transaction.atomic():
            item = Inventory.objects.create(organization=organization, **validated_data)
            logger.info('Inventory item created: %d (%s)', item.id, item.catalog_type)
            return item

    @staticmethod
    def update_item(item, validated_data):
        for attr, value in validated_data.items():
            setattr(item, attr, value)
        item.save()
        return item

    @staticmethod
    def deactivate_item(item):
        item.is_active = False
        item.save(update_fields=['is_active'])
        return item
