"""Business logic for users and organizations."""
import logging

from django.db import transaction

from .models import Organization, SignupRequest, User

logger = logging.getLogger(__name__)


class OrganizationService:
    """Handles organization CRUD and status/module management."""

    @staticmethod
    def list_organizations(filters=None):
        qs = Organization.objects.all()
        if filters:
            if filters.get('status'):
                qs = qs.filter(status=filters['status'])
        return qs

    @staticmethod
    def create_organization(validated_data):
        with transaction.atomic():
            org = Organization.objects.create(**validated_data)
            logger.info('Organization created: %s', org.id)
            return org

    @staticmethod
    def update_organization(org, validated_data):
        for attr, value in validated_data.items():
            setattr(org, attr, value)
        org.save()
        return org

    @staticmethod
    def update_status(org, status):
        org.status = status
        org.save(update_fields=['status', 'updated_at'])
        return org

    @staticmethod
    def update_modules(org, allowed_modules):
        org.allowed_modules = allowed_modules
        org.save(update_fields=['allowed_modules', 'updated_at'])
        return org

    @staticmethod
    def update_settings_tabs(org, allowed_settings_tabs):
        org.allowed_settings_tabs = allowed_settings_tabs
        org.save(update_fields=['allowed_settings_tabs', 'updated_at'])
        return org

    @staticmethod
    def update_industry(org, industry_type, terminology):
        org.industry_type = industry_type
        org.terminology = terminology
        org.save(update_fields=['industry_type', 'terminology', 'updated_at'])
        return org


class UserService:
    """Handles user CRUD within an organization."""

    @staticmethod
    def list_users(organization, filters=None):
        qs = User.objects.filter(organization=organization).exclude(role='super_admin')
        if filters:
            if filters.get('role'):
                qs = qs.filter(role=filters['role'])
            if filters.get('status'):
                qs = qs.filter(status=filters['status'])
        return qs

    @staticmethod
    def get_user(user_id, organization):
        return User.objects.get(pk=user_id, organization=organization)

    @staticmethod
    def create_user(serializer, organization):
        return serializer.save(organization=organization)

    @staticmethod
    def deactivate_user(user):
        user.status = User.STATUS_INACTIVE
        user.save(update_fields=['status'])
        return user

    @staticmethod
    def delete_user(user):
        user.delete()


class SuperAdminUserService:
    """Handles super_admin user management."""

    @staticmethod
    def list_super_admins():
        return User.objects.filter(role='super_admin', organization__isnull=True)

    @staticmethod
    def create_super_admin(serializer):
        return serializer.save(organization=None, role='super_admin')


class SignupRequestService:
    @staticmethod
    def list():
        return SignupRequest.objects.all()

    @staticmethod
    def create(validated_data):
        return SignupRequest.objects.create(**validated_data)

    @staticmethod
    def delete(instance):
        instance.delete()
