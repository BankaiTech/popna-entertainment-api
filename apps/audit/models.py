"""
AuditLog model — tracks all entity changes.
SMS logs stored as entity_type='sms'.
"""
from django.db import models

from apps.users.models import Organization, User


class AuditLog(models.Model):
    """
    Unified audit trail + SMS log.
    entity_type='sms' with meta = { contactId, mobile, message, smsType, status, ... }
    """

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        db_column='organization_id',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    username = models.CharField(max_length=100, null=True, blank=True)
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=50, null=True, blank=True)
    action = models.CharField(max_length=50)
    meta = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_log'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'entity_type', 'entity_id']),
            models.Index(fields=['organization', 'created_at']),
        ]

    def __str__(self):
        return f'{self.entity_type}:{self.entity_id} — {self.action}'
