"""Business logic for Audit Log and SMS."""
import logging
import requests

from django.conf import settings

from .models import AuditLog

logger = logging.getLogger(__name__)


class AuditLogService:

    @staticmethod
    def log(organization, action, entity_type, entity_id=None, user=None, meta=None):
        """Create an audit log entry. Called internally after create/update/delete."""
        try:
            AuditLog.objects.create(
                organization=organization,
                user=user,
                username=user.username if user else None,
                entity_type=entity_type,
                entity_id=str(entity_id) if entity_id else None,
                action=action,
                meta=meta or {},
            )
        except Exception as exc:
            logger.exception('Failed to write audit log: %s', exc)

    @staticmethod
    def list_logs(organization, filters=None):
        qs = AuditLog.objects.filter(organization=organization)
        if not filters:
            return qs
        if filters.get('entityType'):
            qs = qs.filter(entity_type=filters['entityType'])
        if filters.get('entityId'):
            qs = qs.filter(entity_id=filters['entityId'])
        if filters.get('userId'):
            qs = qs.filter(user_id=filters['userId'])
        if filters.get('from'):
            qs = qs.filter(created_at__date__gte=filters['from'])
        if filters.get('to'):
            qs = qs.filter(created_at__date__lte=filters['to'])
        return qs

    @staticmethod
    def list_sms_logs(organization, filters=None):
        qs = AuditLog.objects.filter(organization=organization, entity_type='sms')
        if not filters:
            return qs
        if filters.get('contactId'):
            qs = qs.filter(meta__contactId=filters['contactId'])
        if filters.get('from'):
            qs = qs.filter(created_at__date__gte=filters['from'])
        if filters.get('to'):
            qs = qs.filter(created_at__date__lte=filters['to'])
        return qs


class SMSService:
    """Sends SMS using the org's configured provider and logs the result."""

    @staticmethod
    def send_sms(organization, mobile, message, sms_type='general', contact_id=None):
        from apps.org_settings.models import OrgSettings

        try:
            org_settings = OrgSettings.objects.get(organization=organization)
        except OrgSettings.DoesNotExist:
            logger.warning('OrgSettings not found for org %s — SMS not sent.', organization.id)
            return False

        if not org_settings.sms_enabled:
            logger.info('SMS disabled for org %s', organization.id)
            return False

        status = 'failed'
        provider_ref = None
        error_message = None

        try:
            # Generic HTTP SMS dispatch — extend per provider as needed
            response = requests.post(
                f'https://api.{org_settings.sms_provider}.com/send',
                json={
                    'apikey': org_settings.sms_api_key,
                    'sender': org_settings.sms_sender_id,
                    'to': mobile,
                    'message': message,
                },
                timeout=10,
            )
            response.raise_for_status()
            provider_ref = response.json().get('id')
            status = 'sent'
        except Exception as exc:
            error_message = str(exc)
            logger.exception('SMS send failed: %s', exc)

        # Write audit log entry
        AuditLogService.log(
            organization=organization,
            action='sms_sent' if status == 'sent' else 'sms_failed',
            entity_type='sms',
            meta={
                'contactId': contact_id,
                'mobile': mobile,
                'message': message,
                'smsType': sms_type,
                'status': status,
                'providerRef': provider_ref,
                'errorMessage': error_message,
            },
        )

        return status == 'sent'
