"""Business logic for Documents."""
import logging
from django.db import transaction
from .models import Document

logger = logging.getLogger(__name__)


class DocumentService:

    @staticmethod
    def list_documents(organization, filters=None):
        qs = Document.objects.filter(organization=organization)
        if not filters:
            return qs
        if filters.get('kind'):
            qs = qs.filter(kind=filters['kind'])
        if filters.get('status'):
            qs = qs.filter(status=filters['status'])
        if filters.get('contactId'):
            qs = qs.filter(contact_id=filters['contactId'])
        return qs

    @staticmethod
    def get_document(doc_id, organization):
        return Document.objects.get(pk=doc_id, organization=organization)

    @staticmethod
    def create_document(validated_data, organization):
        with transaction.atomic():
            doc = Document.objects.create(organization=organization, **validated_data)
            logger.info('Document created: %d (%s)', doc.id, doc.kind)
            return doc

    @staticmethod
    def update_document(document, validated_data):
        for attr, value in validated_data.items():
            setattr(document, attr, value)
        document.save()
        return document

    @staticmethod
    def delete_document(document):
        document.delete()
