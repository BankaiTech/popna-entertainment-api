"""Business logic for Invoices."""
import logging

from django.db import transaction

from .models import Invoice

logger = logging.getLogger(__name__)


class InvoiceService:

    @staticmethod
    def list_invoices(organization, filters=None):
        qs = Invoice.objects.filter(organization=organization).select_related('contact')

        if not filters:
            return qs

        if filters.get('kind'):
            qs = qs.filter(kind=filters['kind'])
        if filters.get('status'):
            qs = qs.filter(status=filters['status'])
        if filters.get('branchId'):
            qs = qs.filter(branch_id=filters['branchId'])
        if filters.get('contactId'):
            qs = qs.filter(contact_id=filters['contactId'])
        if filters.get('from'):
            qs = qs.filter(issue_date__gte=filters['from'])
        if filters.get('to'):
            qs = qs.filter(issue_date__lte=filters['to'])

        return qs

    @staticmethod
    def get_invoice(invoice_id, organization):
        return Invoice.objects.select_related('contact').get(
            pk=invoice_id, organization=organization
        )

    @staticmethod
    def create_invoice(validated_data, organization):
        with transaction.atomic():
            invoice = Invoice.objects.create(organization=organization, **validated_data)
            logger.info('Invoice created: %d (%s)', invoice.id, invoice.kind)
            return invoice

    @staticmethod
    def update_invoice(invoice, validated_data):
        for attr, value in validated_data.items():
            setattr(invoice, attr, value)
        invoice.save()
        return invoice

    @staticmethod
    def void_or_delete(invoice):
        if invoice.status == Invoice.STATUS_DRAFT:
            invoice.delete()
        else:
            invoice.status = Invoice.STATUS_VOIDED
            invoice.save(update_fields=['status', 'updated_at'])
