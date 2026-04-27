"""Root URL configuration for Popna."""
from django.urls import include, path

urlpatterns = [
    # Authentication & Users
    path('api/', include('apps.users.urls')),

    # Contacts
    path('api/', include('apps.contacts.urls')),

    # Inventory (unified catalog + aliases)
    path('api/', include('apps.inventory.urls')),

    # Activities
    path('api/', include('apps.activities.urls')),

    # Invoices (+ POS aliases)
    path('api/', include('apps.invoices.urls')),

    # Documents
    path('api/', include('apps.documents.urls')),

    # Subscriptions
    path('api/', include('apps.subscriptions.urls')),

    # Settings (+ company-profile / website-settings aliases)
    path('api/', include('apps.org_settings.urls')),

    # Audit Log & SMS
    path('api/', include('apps.audit.urls')),

    # Dashboard & Reports
    path('api/', include('apps.dashboard.urls')),
]
