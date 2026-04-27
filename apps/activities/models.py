"""
Activity model — single table for all activity types.
kind discriminates: complaint | connection_request | appointment | service_request | lead
payload JSONB holds all kind-specific fields.
"""
from django.db import models

from apps.contacts.models import Contact
from apps.users.models import Organization


class Activity(models.Model):
    KIND_COMPLAINT = 'complaint'
    KIND_CONNECTION_REQUEST = 'connection_request'
    KIND_APPOINTMENT = 'appointment'
    KIND_SERVICE_REQUEST = 'service_request'
    KIND_LEAD = 'lead'
    KIND_CHOICES = [
        (KIND_COMPLAINT, 'Complaint'),
        (KIND_CONNECTION_REQUEST, 'Connection Request'),
        (KIND_APPOINTMENT, 'Appointment'),
        (KIND_SERVICE_REQUEST, 'Service Request'),
        (KIND_LEAD, 'Lead'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='activities',
        db_column='organization_id',
    )
    kind = models.CharField(max_length=30, choices=KIND_CHOICES)
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities',
    )
    status = models.CharField(max_length=50, default='new')
    priority = models.CharField(max_length=20, null=True, blank=True)
    assigned_to = models.CharField(max_length=255, null=True, blank=True)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'kind']),
            models.Index(fields=['organization', 'kind', 'status']),
            models.Index(fields=['contact']),
        ]

    def __str__(self):
        return f'{self.kind} #{self.id} [{self.status}]'
