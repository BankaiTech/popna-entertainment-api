from django.urls import path
from .views import (
    CustomerInvoicesView,
    InvoiceDetailView,
    InvoiceListCreateView,
    POSDetailView,
    POSListCreateView,
)

urlpatterns = [
    # Core
    path('invoices', InvoiceListCreateView.as_view(), name='invoice-list-create'),
    path('invoices/<int:invoice_id>', InvoiceDetailView.as_view(), name='invoice-detail'),

    # Customer portal
    path('customer/invoices', CustomerInvoicesView.as_view(), name='customer-invoices'),

    # POS aliases
    path('pos', POSListCreateView.as_view(), name='pos-list-create'),
    path('pos/<int:invoice_id>', POSDetailView.as_view(), name='pos-detail'),
]
