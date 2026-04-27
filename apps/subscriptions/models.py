"""Subscription model — recurring billing for contacts."""
from django.db import models

from apps.contacts.models import Contact
from apps.users.models import Organization


class Subscription(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_CANCELLED = 'cancelled'
    STATUS_EXPIRED = 'expired'
    STATUS_PAUSED = 'paused'

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        db_column='organization_id',
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    plan_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(max_length=20, default='monthly')
    start_date = models.DateField()
    next_billing_date = models.DateField()
    status = models.CharField(max_length=20, default=STATUS_ACTIVE)
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subscriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['contact']),
            models.Index(fields=['next_billing_date']),
        ]

    def __str__(self):
        return f'{self.plan_name} — {self.contact}'
