"""Contact model — customers, suppliers, and vendors in one table."""
from django.db import models

from apps.users.models import Organization


class Contact(models.Model):
    """
    Single table for all contact types (customer / supplier / vendor).
    contact_type discriminates the purpose.
    password_hash enables customer portal login.
    """

    TYPE_CUSTOMER = 'customer'
    TYPE_SUPPLIER = 'supplier'
    TYPE_VENDOR = 'vendor'
    TYPE_CHOICES = [
        (TYPE_CUSTOMER, 'Customer'),
        (TYPE_SUPPLIER, 'Supplier'),
        (TYPE_VENDOR, 'Vendor'),
    ]

    STATUS_ACTIVE = 'Active'
    STATUS_INACTIVE = 'Inactive'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    ]

    PAYMENT_PAID = 'paid'
    PAYMENT_NOT_PAID = 'not_paid'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PAID, 'Paid'),
        (PAYMENT_NOT_PAID, 'Not Paid'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='contacts',
        db_column='organization_id',
    )
    contact_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_CUSTOMER)

    # Core fields
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    mobile = models.CharField(max_length=20)
    gstin = models.CharField(max_length=20, null=True, blank=True)

    # Address
    address_line1 = models.CharField(max_length=255, null=True, blank=True)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, default='India')
    pincode = models.CharField(max_length=10, null=True, blank=True)
    additional_addresses = models.JSONField(default=list)

    # Customer portal
    password_hash = models.CharField(max_length=255, null=True, blank=True)

    # ISP / customer-specific
    connection_type = models.CharField(max_length=100, null=True, blank=True)
    package = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_NOT_PAID
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    collected_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    collected_by_username = models.CharField(max_length=100, null=True, blank=True)
    box_number = models.CharField(max_length=50, null=True, blank=True)
    stb_number = models.CharField(max_length=100, null=True, blank=True)
    can_caf_id = models.CharField(max_length=100, null=True, blank=True)
    cin = models.CharField(max_length=100, null=True, blank=True)
    area = models.CharField(max_length=100, null=True, blank=True)
    permanent_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    branch_id = models.IntegerField(null=True, blank=True)
    payment_description = models.TextField(null=True, blank=True)
    payment_updated_at = models.DateTimeField(null=True, blank=True)

    # Supplier / Vendor
    contact_person = models.CharField(max_length=255, null=True, blank=True)
    tax_number = models.CharField(max_length=30, null=True, blank=True)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Universal multi-industry fields
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    loyalty_points = models.IntegerField(default=0)
    tags = models.JSONField(default=list)
    custom_fields = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contacts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'contact_type']),
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['organization', 'payment_status']),
            models.Index(fields=['organization', 'mobile']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'contact_type', 'mobile'],
                name='unique_org_type_mobile',
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.contact_type})'
