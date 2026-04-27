"""Views for Audit Log and SMS."""
import logging
from rest_framework import status
from rest_framework.views import APIView
from common.permissions.permissions import IsOrgMember
from common.utils.pagination import StandardResultsSetPagination
from common.utils.responses import created_response, error_response, success_response
from .serializers import AuditLogCreateSerializer, AuditLogSerializer
from .services import AuditLogService, SMSService

logger = logging.getLogger(__name__)


class AuditLogListView(APIView):
    """GET /audit-log  POST /audit-log"""
    permission_classes = (IsOrgMember,)

    def get(self, request):
        qs = AuditLogService.list_logs(request.user.organization, request.query_params)
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(AuditLogSerializer(page, many=True).data)

    def post(self, request):
        """Internal endpoint — append a manual audit entry."""
        serializer = AuditLogCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AuditLogService.log(
            organization=request.user.organization,
            action=serializer.validated_data['action'],
            entity_type=serializer.validated_data['entity_type'],
            entity_id=serializer.validated_data.get('entity_id'),
            user=request.user,
            meta=serializer.validated_data.get('meta', {}),
        )
        return created_response(message='Audit entry recorded.')


class SMSLogListView(APIView):
    """GET /sms-logs"""
    permission_classes = (IsOrgMember,)

    def get(self, request):
        qs = AuditLogService.list_sms_logs(request.user.organization, request.query_params)
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(AuditLogSerializer(page, many=True).data)


class SMSSendView(APIView):
    """POST /sms/send"""
    permission_classes = (IsOrgMember,)

    def post(self, request):
        mobile = request.data.get('mobile')
        message = request.data.get('message')
        sms_type = request.data.get('smsType', 'general')
        contact_id = request.data.get('contactId')

        if not mobile or not message:
            return error_response('mobile and message are required.')

        sent = SMSService.send_sms(
            organization=request.user.organization,
            mobile=mobile,
            message=message,
            sms_type=sms_type,
            contact_id=contact_id,
        )

        if sent:
            return success_response(message='SMS sent successfully.')
        return error_response('SMS could not be sent.', http_status=status.HTTP_502_BAD_GATEWAY)
