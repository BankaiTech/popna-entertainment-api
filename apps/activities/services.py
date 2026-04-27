"""Business logic for Activities."""
import logging

from django.db import transaction

from .models import Activity

logger = logging.getLogger(__name__)


class ActivityService:

    @staticmethod
    def list_activities(organization, filters=None):
        qs = Activity.objects.filter(organization=organization).select_related('contact')

        if not filters:
            return qs

        if filters.get('kind'):
            qs = qs.filter(kind=filters['kind'])
        if filters.get('status'):
            qs = qs.filter(status=filters['status'])
        if filters.get('contactId'):
            qs = qs.filter(contact_id=filters['contactId'])
        if filters.get('priority'):
            qs = qs.filter(priority=filters['priority'])
        if filters.get('assigned_to'):
            qs = qs.filter(assigned_to__icontains=filters['assigned_to'])

        return qs

    @staticmethod
    def get_activity(activity_id, organization):
        return Activity.objects.select_related('contact').get(
            pk=activity_id, organization=organization
        )

    @staticmethod
    def create_activity(validated_data, organization):
        with transaction.atomic():
            activity = Activity.objects.create(organization=organization, **validated_data)
            logger.info('Activity created: %d (%s)', activity.id, activity.kind)
            return activity

    @staticmethod
    def update_activity(activity, validated_data):
        for attr, value in validated_data.items():
            setattr(activity, attr, value)
        activity.save()
        return activity

    @staticmethod
    def delete_activity(activity):
        activity.delete()
