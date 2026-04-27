"""Role-based permissions for Popna API."""
from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    """Allows access only to super_admin users (organization_id is NULL)."""

    message = 'Super admin access required.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'super_admin'
        )


class IsOrgAdmin(BasePermission):
    """Allows access to admin (or above) users scoped to an organization."""

    message = 'Organization admin access required.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ('admin', 'super_admin')
            and request.user.organization_id is not None
        )


class IsOrgMember(BasePermission):
    """Allows access to any authenticated org user (admin or employee)."""

    message = 'Organization membership required.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.organization_id is not None
        )


class IsCustomer(BasePermission):
    """Allows access to authenticated customers (contact-based JWT)."""

    message = 'Customer authentication required.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'is_customer', False)
        )


class IsOrgAdminOrReadOnly(BasePermission):
    """Read-only for org members, write for org admins."""

    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return (
                request.user
                and request.user.is_authenticated
                and request.user.organization_id is not None
            )
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ('admin', 'super_admin')
            and request.user.organization_id is not None
        )
