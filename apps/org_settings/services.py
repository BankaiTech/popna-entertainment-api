"""Business logic for OrgSettings."""
import logging
from .models import OrgSettings

logger = logging.getLogger(__name__)


class OrgSettingsService:

    @staticmethod
    def get_or_create(organization):
        settings, _ = OrgSettings.objects.get_or_create(organization=organization)
        return settings

    @staticmethod
    def update_settings(settings, validated_data):
        for attr, value in validated_data.items():
            setattr(settings, attr, value)
        settings.save()
        return settings

    @staticmethod
    def update_custom_fields(settings, schema):
        settings.custom_field_schema = schema
        settings.save(update_fields=['custom_field_schema', 'updated_at'])
        return settings

    @staticmethod
    def update_website(settings, website_data):
        settings.website = website_data
        settings.save(update_fields=['website', 'updated_at'])
        return settings
