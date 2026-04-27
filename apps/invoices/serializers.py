"""Serializers for Invoice."""
from rest_framework import serializers

from .models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'organization')

    def validate(self, attrs):
        # Compute totals from items if not explicitly provided
        items = attrs.get('items', [])
        if items and not attrs.get('total_amount'):
            subtotal = sum(
                float(i.get('unitPrice', 0)) * float(i.get('quantity', 1))
                for i in items
            )
            tax_total = sum(
                float(i.get('unitPrice', 0)) * float(i.get('quantity', 1))
                * float(i.get('taxRate', 0)) / 100
                for i in items
            )
            discount = sum(float(i.get('discount', 0)) for i in items)
            attrs.setdefault('subtotal', round(subtotal, 2))
            attrs.setdefault('tax_total', round(tax_total, 2))
            attrs.setdefault('discount_amount', round(discount, 2))
            attrs.setdefault('total_amount', round(subtotal + tax_total - discount, 2))
        return attrs


class InvoiceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = (
            'id', 'kind', 'invoice_number', 'status', 'issue_date',
            'due_date', 'customer_name', 'vendor_name', 'total_amount',
            'contact_id', 'branch_id', 'created_at',
        )
