"""Settings URLs + backward-compatible aliases."""
from django.urls import path
from .views import BranchesView, CustomFieldsView, SettingsView, WebsiteSettingsView

urlpatterns = [
    # Core settings
    path('settings', SettingsView.as_view(), name='settings'),
    path('settings/custom-fields', CustomFieldsView.as_view(), name='settings-custom-fields'),
    path('settings/branches', BranchesView.as_view(), name='settings-branches'),
    path('settings/website', WebsiteSettingsView.as_view(), name='settings-website'),

    # Aliases: company-profile
    path('company-profile', SettingsView.as_view(), name='company-profile'),
    path('company-profile/custom-fields', CustomFieldsView.as_view(), name='company-profile-custom-fields'),
    path('company-profile/branches', BranchesView.as_view(), name='company-profile-branches'),

    # Aliases: website-settings
    path('website-settings', WebsiteSettingsView.as_view(), name='website-settings'),
]
