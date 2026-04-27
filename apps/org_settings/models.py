"""
OrgSettings model — one row per organization.
Stores company profile, branches, SMS config, UPI config,
custom field schema, and website JSONB.
"""
from django.db import models

from apps.users.models import Organization


class OrgSettings(models.Model):
    """Single-row-per-org settings table."""

    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='settings',
        db_column='organization_id',
    )

    # Company profile
    company_name = models.CharField(max_length=255, default='')
    gstin = models.CharField(max_length=20, null=True, blank=True)
    address_line1 = models.CharField(max_length=255, null=True, blank=True)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, default='India')
    pincode = models.CharField(max_length=10, null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    # Branches
    branches = models.JSONField(default=list)

    # SMS config
    sms_enabled = models.BooleanField(default=False)
    sms_provider = models.CharField(max_length=50, default='')
    sms_api_key = models.CharField(max_length=255, default='')
    sms_sender_id = models.CharField(max_length=20, default='')
    sms_template_id = models.CharField(max_length=100, default='')
    sms_templates = models.JSONField(default=dict)

    # UPI config
    upi_id = models.CharField(max_length=100, default='')
    upi_display_name = models.CharField(max_length=255, default='')
    upi_enabled = models.BooleanField(default=False)
    upi_supported_apps = models.JSONField(default=list)

    # Custom fields schema
    custom_field_schema = models.JSONField(default=list)

    # Website settings (atomically read/written as JSONB blob)
    website = models.JSONField(default=dict)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'settings'

    def __str__(self):
        return f'Settings for {self.organization_id}'
