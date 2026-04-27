"""
Invoice model — unified table for sales, purchase, and POS invoices.
Line items stored as JSON. Kind-specific data in payload JSON.
"""
from django.db import models

from apps.contacts.models import Contact
from apps.users.models import Organization


class Invoice(models.Model):
    KIND_SALES = 'sales'
    KIND_PURCHASE = 'purchase'
    KIND_POS = 'pos'
    KIND_CHOICES = [
        (KIND_SALES, 'Sales'),
        (KIND_PURCHASE, 'Purchase'),
        (KIND_POS, 'POS'),
    ]

    STATUS_DRAFT = 'draft'
    STATUS_SENT = 'sent'
    STATUS_PAID = 'paid'
    STATUS_OVERDUE = 'overdue'
    STATUS_COMPLETED = 'completed'
    STATUS_REFUNDED = 'refunded'
    STATUS_VOIDED = 'voided'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SENT, 'Sent'),
        (STATUS_PAID, 'Paid'),
        (STATUS_OVERDUE, 'Overdue'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_REFUNDED, 'Refunded'),
        (STATUS_VOIDED, 'Voided'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='invoices',
        db_column='organization_id',
    )
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    invoice_number = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    issue_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)

    # Parties
    branch_id = models.IntegerField(null=True, blank=True)
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
    )
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    vendor_name = models.CharField(max_length=255, null=True, blank=True)

    # Financials
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Line items (JSON array)
    items = models.JSONField(default=list)

    # Kind-specific data
    payload = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'kind']),
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['contact']),
            models.Index(fields=['organization', 'issue_date']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'invoice_number'],
                name='unique_org_invoice_number',
            )
        ]

    def __str__(self):
        return f'{self.invoice_number} ({self.kind})'
