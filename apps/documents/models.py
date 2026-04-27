"""Document model — quotations, purchase orders, expenses."""
from django.db import models

from apps.contacts.models import Contact
from apps.users.models import Organization


class Document(models.Model):
    KIND_QUOTATION = 'quotation'
    KIND_PURCHASE_ORDER = 'purchase_order'
    KIND_EXPENSE = 'expense'
    KIND_CHOICES = [
        (KIND_QUOTATION, 'Quotation'),
        (KIND_PURCHASE_ORDER, 'Purchase Order'),
        (KIND_EXPENSE, 'Expense'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='documents',
        db_column='organization_id',
    )
    kind = models.CharField(max_length=30, choices=KIND_CHOICES)
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents_as_contact',
        db_column='contact_id',
    )
    vendor = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents_as_vendor',
        db_column='vendor_id',
    )
    document_number = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='draft')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    items = models.JSONField(default=list)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'kind']),
            models.Index(fields=['organization', 'kind', 'status']),
            models.Index(fields=['contact']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'kind', 'document_number'],
                name='unique_org_kind_document_number',
            )
        ]

    def __str__(self):
        return f'{self.document_number} ({self.kind})'
