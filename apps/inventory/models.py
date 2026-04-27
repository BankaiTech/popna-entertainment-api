"""
Inventory model — unified catalog.

catalog_type discriminates between:
  'product'      — general/physical products
  'isp_category' — ISP service categories (Cable, Internet 1 …)
  'isp_plan'     — ISP pricing plans
"""
from django.db import models

from apps.users.models import Organization


class Inventory(models.Model):
    CATALOG_PRODUCT = 'product'
    CATALOG_ISP_CATEGORY = 'isp_category'
    CATALOG_ISP_PLAN = 'isp_plan'
    CATALOG_CHOICES = [
        (CATALOG_PRODUCT, 'Product'),
        (CATALOG_ISP_CATEGORY, 'ISP Category'),
        (CATALOG_ISP_PLAN, 'ISP Plan'),
    ]

    FORM_PHYSICAL = 'physical'
    FORM_SERVICE = 'service'
    FORM_DIGITAL = 'digital'
    FORM_BUNDLE = 'bundle'
    FORM_CHOICES = [
        (FORM_PHYSICAL, 'Physical'),
        (FORM_SERVICE, 'Service'),
        (FORM_DIGITAL, 'Digital'),
        (FORM_BUNDLE, 'Bundle'),
    ]

    TAX_INCLUSIVE = 'inclusive'
    TAX_EXCLUSIVE = 'exclusive'
    TAX_NONE = 'none'
    TAX_CHOICES = [
        (TAX_INCLUSIVE, 'Inclusive'),
        (TAX_EXCLUSIVE, 'Exclusive'),
        (TAX_NONE, 'None'),
    ]

    TRACKING_NONE = 'none'
    TRACKING_SERIAL = 'serial'
    TRACKING_BATCH = 'batch'
    TRACKING_CHOICES = [
        (TRACKING_NONE, 'None'),
        (TRACKING_SERIAL, 'Serial'),
        (TRACKING_BATCH, 'Batch'),
    ]

    WEIGHT_G = 'g'
    WEIGHT_KG = 'kg'
    WEIGHT_LB = 'lb'
    WEIGHT_CHOICES = [
        (WEIGHT_G, 'Grams'),
        (WEIGHT_KG, 'Kilograms'),
        (WEIGHT_LB, 'Pounds'),
    ]

    DURATION_DAYS = 'days'
    DURATION_MONTHS = 'months'
    DURATION_YEARS = 'years'
    DURATION_CHOICES = [
        (DURATION_DAYS, 'Days'),
        (DURATION_MONTHS, 'Months'),
        (DURATION_YEARS, 'Years'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='inventory_items',
        db_column='organization_id',
    )
    catalog_type = models.CharField(max_length=20, choices=CATALOG_CHOICES, default=CATALOG_PRODUCT)

    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    category_code = models.CharField(max_length=50, null=True, blank=True)
    subcategory = models.CharField(max_length=255, null=True, blank=True)
    unit = models.CharField(max_length=50, null=True, blank=True)
    unit_short_name = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Product classification
    product_form = models.CharField(max_length=20, choices=FORM_CHOICES, default=FORM_PHYSICAL, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    hsn_sac_code = models.CharField(max_length=20, null=True, blank=True)

    # Tax
    tax_type = models.CharField(max_length=20, choices=TAX_CHOICES, default=TAX_EXCLUSIVE)
    tax_rate_name = models.CharField(max_length=100, null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Warranty
    warranty_name = models.CharField(max_length=100, null=True, blank=True)
    warranty_duration = models.IntegerField(null=True, blank=True)
    warranty_unit = models.CharField(max_length=20, choices=DURATION_CHOICES, default=DURATION_MONTHS, null=True, blank=True)

    # Stock (catalog_type='product' only)
    current_stock = models.IntegerField(default=0)
    stock_alert = models.IntegerField(null=True, blank=True)
    reorder_level = models.IntegerField(null=True, blank=True)
    tracking_type = models.CharField(max_length=20, choices=TRACKING_CHOICES, default=TRACKING_NONE)
    barcode = models.CharField(max_length=100, null=True, blank=True)
    weight = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    weight_unit = models.CharField(max_length=5, choices=WEIGHT_CHOICES, null=True, blank=True)
    expiry_tracking = models.BooleanField(default=False)
    branch_id = models.IntegerField(null=True, blank=True)
    batch_number = models.CharField(max_length=100, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    variants = models.JSONField(default=list)

    # Kind-specific metadata
    meta = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inventory'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'catalog_type']),
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['organization', 'category']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'sku'],
                name='unique_org_sku',
                condition=models.Q(sku__isnull=False),
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.catalog_type})'
