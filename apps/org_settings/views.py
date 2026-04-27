"""Views for Settings + company-profile / website-settings aliases."""
import logging
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from common.permissions.permissions import IsOrgAdmin, IsOrgMember
from common.utils.responses import success_response
from .serializers import (
    BranchesSerializer,
    CustomFieldSchemaSerializer,
    OrgSettingsSerializer,
    WebsiteSettingsSerializer,
)
from .services import OrgSettingsService

logger = logging.getLogger(__name__)


class SettingsView(APIView):
    """GET /settings  PATCH /settings"""
    permission_classes = (IsOrgMember,)

    def get(self, request):
        settings = OrgSettingsService.get_or_create(request.user.organization)
        return success_response(data=OrgSettingsSerializer(settings).data)

    def patch(self, request):
        settings = OrgSettingsService.get_or_create(request.user.organization)
        serializer = OrgSettingsSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        settings = OrgSettingsService.update_settings(settings, serializer.validated_data)
        return success_response(data=OrgSettingsSerializer(settings).data)


class CustomFieldsView(APIView):
    """PATCH /settings/custom-fields"""
    permission_classes = (IsOrgAdmin,)

    def patch(self, request):
        settings = OrgSettingsService.get_or_create(request.user.organization)
        serializer = CustomFieldSchemaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        settings = OrgSettingsService.update_custom_fields(
            settings, serializer.validated_data['custom_field_schema']
        )
        return success_response(data=CustomFieldSchemaSerializer(settings).data)


class BranchesView(APIView):
    """GET /settings/branches"""
    permission_classes = (IsOrgMember,)

    def get(self, request):
        settings = OrgSettingsService.get_or_create(request.user.organization)
        return success_response(data=BranchesSerializer(settings).data)


class WebsiteSettingsView(APIView):
    """GET /settings/website  PATCH /settings/website"""

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsOrgAdmin()]

    def get(self, request):
        from apps.users.models import Organization
        org_id = request.query_params.get('orgId')
        if org_id:
            try:
                org = Organization.objects.get(pk=org_id)
                settings = OrgSettingsService.get_or_create(org)
            except Organization.DoesNotExist:
                return success_response(data={})
        elif request.user.is_authenticated and not getattr(request.user, 'is_customer', False):
            settings = OrgSettingsService.get_or_create(request.user.organization)
        else:
            return success_response(data={})
        return success_response(data=WebsiteSettingsSerializer(settings).data)

    def patch(self, request):
        settings = OrgSettingsService.get_or_create(request.user.organization)
        serializer = WebsiteSettingsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        settings = OrgSettingsService.update_website(
            settings, serializer.validated_data['website']
        )
        return success_response(data=WebsiteSettingsSerializer(settings).data)
