"""Business logic for contacts."""
import logging

from django.db import transaction

from .models import Contact

logger = logging.getLogger(__name__)


class ContactService:
    """CRUD + filtering for contacts."""

    @staticmethod
    def list_contacts(organization, filters=None):
        qs = Contact.objects.filter(organization=organization)

        if not filters:
            return qs

        if filters.get('type'):
            qs = qs.filter(contact_type=filters['type'])
        if filters.get('status'):
            qs = qs.filter(status=filters['status'])
        if filters.get('paymentStatus'):
            qs = qs.filter(payment_status=filters['paymentStatus'])
        if filters.get('area'):
            qs = qs.filter(area__icontains=filters['area'])
        if filters.get('branch_id'):
            qs = qs.filter(branch_id=filters['branch_id'])
        if filters.get('search'):
            from django.db.models import Q
            term = filters['search']
            qs = qs.filter(
                Q(name__icontains=term)
                | Q(mobile__icontains=term)
                | Q(email__icontains=term)
                | Q(area__icontains=term)
            )

        return qs

    @staticmethod
    def get_contact(contact_id, organization):
        return Contact.objects.get(pk=contact_id, organization=organization)

    @staticmethod
    def create_contact(validated_data, organization):
        with transaction.atomic():
            contact = Contact.objects.create(organization=organization, **validated_data)
            logger.info('Contact created: %d in org %s', contact.id, organization.id)
            return contact

    @staticmethod
    def update_contact(contact, validated_data):
        for attr, value in validated_data.items():
            setattr(contact, attr, value)
        contact.save()
        return contact

    @staticmethod
    def delete_contact(contact):
        contact.delete()
