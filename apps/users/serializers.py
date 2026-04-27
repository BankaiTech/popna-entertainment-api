"""Serializers for auth, users, organizations, and signup requests."""
import logging

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Organization, SignupRequest, User

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# JWT — Custom token claims
# ---------------------------------------------------------------------------

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Overrides default JWT serializer to:
    1. Support username-based login (not id).
    2. Support customer login via contact model.
    3. Inject custom claims: role, organization_id, name.
    """

    username_field = 'username'

    def validate(self, attrs):
        from apps.contacts.models import Contact
        username = attrs.get('username')
        password = attrs.get('password')
        organization_id = attrs.get('organization_id')

        # Try customer login first if organization_id present and no matching user
        user = self._authenticate_user(username, password, organization_id)
        if user is None:
            user = self._authenticate_customer(username, password, organization_id)

        if user is None:
            raise serializers.ValidationError('Invalid username or password.')

        if not user.is_active:
            raise serializers.ValidationError('This account has been deactivated.')

        refresh = RefreshToken.for_user(user)
        self._add_custom_claims(refresh, user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': self._build_user_data(user),
        }

    def _authenticate_user(self, username, password, organization_id):
        """Find and verify a User record."""
        base_qs = User.objects.filter(username=username)

        # If organization is specified, enforce it.
        if organization_id:
            user = base_qs.filter(organization_id=organization_id).first()
            if user and user.check_password(password):
                return user
            return None

        # When org isn't provided, try super-admin first (org NULL),
        # then fall back to any user with that username.
        super_admin = base_qs.filter(organization__isnull=True).first()
        if super_admin and super_admin.check_password(password):
            return super_admin

        user = base_qs.exclude(organization__isnull=True).first()
        if user and user.check_password(password):
            return user

        return None

    def _authenticate_customer(self, username, password, organization_id):
        """Find and verify a Contact record (customer portal login)."""
        from apps.contacts.models import Contact
        from apps.users.tokens import CustomerUser

        qs = Contact.objects.filter(
            mobile=username,
            contact_type='customer',
        )
        if organization_id:
            qs = qs.filter(organization_id=organization_id)

        contact = qs.first()
        if contact and contact.password_hash:
            from django.contrib.auth.hashers import check_password
            if check_password(password, contact.password_hash):
                return CustomerUser(contact)
        return None

    def _add_custom_claims(self, refresh, user):
        """Add role, org, name to both access and refresh tokens."""
        from apps.users.tokens import CustomerUser
        if isinstance(user, CustomerUser):
            refresh['is_customer'] = True
            refresh['contact_id'] = user.contact.id
            refresh['organization_id'] = user.contact.organization_id
        else:
            refresh['is_customer'] = False
            refresh['role'] = user.role
            refresh['organization_id'] = user.organization_id
            refresh['name'] = user.name

    def _build_user_data(self, user):
        from apps.users.tokens import CustomerUser
        if isinstance(user, CustomerUser):
            return {
                'id': user.contact.id,
                'name': user.contact.name,
                'mobile': user.contact.mobile,
                'is_customer': True,
                'organization_id': user.contact.organization_id,
            }
        return {
            'id': user.id,
            'name': user.name,
            'username': user.username,
            'role': user.role,
            'organization_id': user.organization_id,
            'allowed_modules': user.allowed_modules,
        }


# ---------------------------------------------------------------------------
# Organization serializers
# ---------------------------------------------------------------------------

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class OrganizationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('status',)


class OrganizationModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('allowed_modules',)


class OrganizationSettingsTabsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('allowed_settings_tabs',)


class OrganizationIndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('industry_type', 'terminology')


# ---------------------------------------------------------------------------
# User serializers
# ---------------------------------------------------------------------------

class UserCreateSerializer(serializers.ModelSerializer):
    """For creating a new user; accepts plain password."""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = (
            'id', 'name', 'username', 'password', 'role',
            'status', 'allowed_modules', 'branch_id', 'allowed_permissions',
        )
        read_only_fields = ('id',)

    def validate_username(self, value):
        org = self.context.get('organization')
        qs = User.objects.filter(username=value, organization=org)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('This username is already taken.')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['organization'] = self.context.get('organization')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, required=False)

    class Meta:
        model = User
        fields = (
            'name', 'password', 'role', 'status',
            'allowed_modules', 'branch_id', 'allowed_permissions',
        )

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'name', 'username', 'role', 'status',
            'allowed_modules', 'branch_id', 'allowed_permissions',
            'organization_id', 'created_at',
        )


# ---------------------------------------------------------------------------
# Signup Request serializers
# ---------------------------------------------------------------------------

class SignupRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignupRequest
        fields = '__all__'
        read_only_fields = ('id', 'created_at')
