"""
Views for: Auth, Users, Organizations, Signup Requests.
All views are thin controllers — business logic lives in services.py.
"""
import logging

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from common.permissions.permissions import IsOrgAdmin, IsOrgMember, IsSuperAdmin
from common.utils.responses import created_response, error_response, success_response

from .models import Organization, SignupRequest, User
from .serializers import (
    CustomTokenObtainPairSerializer,
    OrganizationIndustrySerializer,
    OrganizationModulesSerializer,
    OrganizationSerializer,
    OrganizationSettingsTabsSerializer,
    OrganizationStatusSerializer,
    SignupRequestSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from .services import (
    OrganizationService,
    SignupRequestService,
    SuperAdminUserService,
    UserService,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class LoginView(TokenObtainPairView):
    """POST /auth/login — unified login for all user types."""
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as exc:
            return error_response(str(exc), http_status=status.HTTP_401_UNAUTHORIZED)
        return success_response(data=serializer.validated_data, message='Login successful.')


class LogoutView(APIView):
    """POST /auth/logout — blacklists the refresh token."""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return error_response('Refresh token is required.')
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return error_response('Invalid or expired token.')
        return success_response(message='Logged out successfully.')


class MeView(APIView):
    """GET /auth/me — returns current user or customer profile."""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        if getattr(user, 'is_customer', False):
            from apps.contacts.serializers import ContactSerializer
            serializer = ContactSerializer(user.contact)
            return success_response(data=serializer.data)
        serializer = UserSerializer(user)
        return success_response(data=serializer.data)


# ---------------------------------------------------------------------------
# Users (org-scoped)
# ---------------------------------------------------------------------------

class UserListCreateView(APIView):
    """GET /users  POST /users"""
    permission_classes = (IsOrgAdmin,)

    def get(self, request):
        users = UserService.list_users(request.user.organization, request.query_params)
        serializer = UserSerializer(users, many=True)
        return success_response(data=serializer.data)

    def post(self, request):
        serializer = UserCreateSerializer(
            data=request.data,
            context={'organization': request.user.organization},
        )
        serializer.is_valid(raise_exception=True)
        user = UserService.create_user(serializer, request.user.organization)
        return created_response(data=UserSerializer(user).data)


class UserDetailView(APIView):
    """GET /users/:id  PATCH /users/:id  DELETE /users/:id"""
    permission_classes = (IsOrgAdmin,)

    def _get_user(self, user_id, request):
        try:
            return UserService.get_user(user_id, request.user.organization)
        except User.DoesNotExist:
            return None

    def get(self, request, user_id):
        user = self._get_user(user_id, request)
        if not user:
            return error_response('User not found.', http_status=status.HTTP_404_NOT_FOUND)
        return success_response(data=UserSerializer(user).data)

    def patch(self, request, user_id):
        user = self._get_user(user_id, request)
        if not user:
            return error_response('User not found.', http_status=status.HTTP_404_NOT_FOUND)
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=UserSerializer(user).data)

    def delete(self, request, user_id):
        user = self._get_user(user_id, request)
        if not user:
            return error_response('User not found.', http_status=status.HTTP_404_NOT_FOUND)
        UserService.deactivate_user(user)
        return success_response(message='User deactivated.')


# ---------------------------------------------------------------------------
# Super Admin — Users
# ---------------------------------------------------------------------------

class SuperAdminUserListCreateView(APIView):
    """GET /superadmin/users  POST /superadmin/users"""
    permission_classes = (IsSuperAdmin,)

    def get(self, request):
        users = SuperAdminUserService.list_super_admins()
        return success_response(data=UserSerializer(users, many=True).data)

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data, context={'organization': None})
        serializer.is_valid(raise_exception=True)
        user = SuperAdminUserService.create_super_admin(serializer)
        return created_response(data=UserSerializer(user).data)


class SuperAdminUserDetailView(APIView):
    """PATCH /superadmin/users/:id"""
    permission_classes = (IsSuperAdmin,)

    def patch(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id, role='super_admin', organization__isnull=True)
        except User.DoesNotExist:
            return error_response('Super admin user not found.', http_status=status.HTTP_404_NOT_FOUND)
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=UserSerializer(user).data)


# ---------------------------------------------------------------------------
# Organizations (super admin)
# ---------------------------------------------------------------------------

class OrganizationListCreateView(APIView):
    """GET /organizations  POST /organizations"""
    permission_classes = (IsSuperAdmin,)

    def get(self, request):
        orgs = OrganizationService.list_organizations(request.query_params)
        return success_response(data=OrganizationSerializer(orgs, many=True).data)

    def post(self, request):
        serializer = OrganizationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        org = OrganizationService.create_organization(serializer.validated_data)
        return created_response(data=OrganizationSerializer(org).data)


class OrganizationDetailView(APIView):
    """GET /organizations/:id  PATCH /organizations/:id"""
    permission_classes = (IsSuperAdmin,)

    def _get_org(self, org_id):
        try:
            return Organization.objects.get(pk=org_id)
        except Organization.DoesNotExist:
            return None

    def get(self, request, org_id):
        org = self._get_org(org_id)
        if not org:
            return error_response('Organization not found.', http_status=status.HTTP_404_NOT_FOUND)
        return success_response(data=OrganizationSerializer(org).data)

    def patch(self, request, org_id):
        org = self._get_org(org_id)
        if not org:
            return error_response('Organization not found.', http_status=status.HTTP_404_NOT_FOUND)
        serializer = OrganizationSerializer(org, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        org = OrganizationService.update_organization(org, serializer.validated_data)
        return success_response(data=OrganizationSerializer(org).data)


class OrganizationStatusView(APIView):
    """PATCH /organizations/:id/status"""
    permission_classes = (IsSuperAdmin,)

    def patch(self, request, org_id):
        try:
            org = Organization.objects.get(pk=org_id)
        except Organization.DoesNotExist:
            return error_response('Organization not found.', http_status=status.HTTP_404_NOT_FOUND)
        serializer = OrganizationStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        org = OrganizationService.update_status(org, serializer.validated_data['status'])
        return success_response(data=OrganizationSerializer(org).data)


class OrganizationModulesView(APIView):
    """PATCH /organizations/:id/modules"""
    permission_classes = (IsSuperAdmin,)

    def patch(self, request, org_id):
        try:
            org = Organization.objects.get(pk=org_id)
        except Organization.DoesNotExist:
            return error_response('Organization not found.', http_status=status.HTTP_404_NOT_FOUND)
        serializer = OrganizationModulesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        org = OrganizationService.update_modules(org, serializer.validated_data['allowed_modules'])
        return success_response(data=OrganizationSerializer(org).data)


class OrganizationSettingsTabsView(APIView):
    """PATCH /organizations/:id/settings-tabs"""
    permission_classes = (IsSuperAdmin,)

    def patch(self, request, org_id):
        try:
            org = Organization.objects.get(pk=org_id)
        except Organization.DoesNotExist:
            return error_response('Organization not found.', http_status=status.HTTP_404_NOT_FOUND)
        serializer = OrganizationSettingsTabsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        org = OrganizationService.update_settings_tabs(
            org, serializer.validated_data['allowed_settings_tabs']
        )
        return success_response(data=OrganizationSerializer(org).data)


class OrganizationIndustryView(APIView):
    """PATCH /organizations/:id/industry"""
    permission_classes = (IsSuperAdmin,)

    def patch(self, request, org_id):
        try:
            org = Organization.objects.get(pk=org_id)
        except Organization.DoesNotExist:
            return error_response('Organization not found.', http_status=status.HTTP_404_NOT_FOUND)
        serializer = OrganizationIndustrySerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        org = OrganizationService.update_industry(
            org,
            serializer.validated_data.get('industry_type', org.industry_type),
            serializer.validated_data.get('terminology', org.terminology),
        )
        return success_response(data=OrganizationSerializer(org).data)


# ---------------------------------------------------------------------------
# Signup Requests
# ---------------------------------------------------------------------------

class SignupRequestListView(APIView):
    """GET /signup-requests  POST /signup-requests"""

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsSuperAdmin()]

    def get(self, request):
        requests = SignupRequestService.list()
        return success_response(data=SignupRequestSerializer(requests, many=True).data)

    def post(self, request):
        serializer = SignupRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = SignupRequestService.create(serializer.validated_data)
        return created_response(
            data=SignupRequestSerializer(instance).data,
            message='Signup request submitted.',
        )


class SignupRequestDeleteView(APIView):
    """DELETE /signup-requests/:id"""
    permission_classes = (IsSuperAdmin,)

    def delete(self, request, request_id):
        try:
            instance = SignupRequest.objects.get(pk=request_id)
        except SignupRequest.DoesNotExist:
            return error_response('Signup request not found.', http_status=status.HTTP_404_NOT_FOUND)
        SignupRequestService.delete(instance)
        return success_response(message='Signup request deleted.')
