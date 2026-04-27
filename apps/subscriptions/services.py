"""Business logic for Subscriptions."""
import logging
from django.db import transaction
from .models import Subscription

logger = logging.getLogger(__name__)


class SubscriptionService:

    @staticmethod
    def list_subscriptions(organization, filters=None):
        qs = Subscription.objects.filter(organization=organization).select_related('contact')
        if not filters:
            return qs
        if filters.get('status'):
            qs = qs.filter(status=filters['status'])
        if filters.get('contactId'):
            qs = qs.filter(contact_id=filters['contactId'])
        return qs

    @staticmethod
    def get_subscription(sub_id, organization):
        return Subscription.objects.select_related('contact').get(
            pk=sub_id, organization=organization
        )

    @staticmethod
    def create_subscription(validated_data, organization):
        with transaction.atomic():
            sub = Subscription.objects.create(organization=organization, **validated_data)
            logger.info('Subscription created: %d', sub.id)
            return sub

    @staticmethod
    def update_subscription(subscription, validated_data):
        for attr, value in validated_data.items():
            setattr(subscription, attr, value)
        subscription.save()
        return subscription

    @staticmethod
    def cancel_subscription(subscription):
        subscription.status = Subscription.STATUS_CANCELLED
        subscription.save(update_fields=['status'])
