"""URL patterns for auth, users, organizations, and signup requests."""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,
    LogoutView,
    MeView,
    OrganizationDetailView,
    OrganizationIndustryView,
    OrganizationListCreateView,
    OrganizationModulesView,
    OrganizationSettingsTabsView,
    OrganizationStatusView,
    SignupRequestDeleteView,
    SignupRequestListView,
    SuperAdminUserDetailView,
    SuperAdminUserListCreateView,
    UserDetailView,
    UserListCreateView,
)

urlpatterns = [
    # Auth
    path('auth/login', LoginView.as_view(), name='auth-login'),
    path('auth/logout', LogoutView.as_view(), name='auth-logout'),
    path('auth/refresh', TokenRefreshView.as_view(), name='auth-refresh'),
    path('auth/me', MeView.as_view(), name='auth-me'),

    # Users (org-scoped)
    path('users', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:user_id>', UserDetailView.as_view(), name='user-detail'),

    # Super Admin — Users
    path('superadmin/users', SuperAdminUserListCreateView.as_view(), name='superadmin-user-list-create'),
    path('superadmin/users/<int:user_id>', SuperAdminUserDetailView.as_view(), name='superadmin-user-detail'),

    # Organizations
    path('organizations', OrganizationListCreateView.as_view(), name='organization-list-create'),
    path('organizations/<str:org_id>', OrganizationDetailView.as_view(), name='organization-detail'),
    path('organizations/<str:org_id>/status', OrganizationStatusView.as_view(), name='organization-status'),
    path('organizations/<str:org_id>/modules', OrganizationModulesView.as_view(), name='organization-modules'),
    path('organizations/<str:org_id>/settings-tabs', OrganizationSettingsTabsView.as_view(), name='organization-settings-tabs'),
    path('organizations/<str:org_id>/industry', OrganizationIndustryView.as_view(), name='organization-industry'),

    # Signup Requests
    path('signup-requests', SignupRequestListView.as_view(), name='signup-request-list'),
    path('signup-requests/<int:request_id>', SignupRequestDeleteView.as_view(), name='signup-request-delete'),
]
