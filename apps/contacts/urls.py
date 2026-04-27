from django.urls import path
from .views import ContactDetailView, ContactListCreateView, CustomerMeView

urlpatterns = [
    path('contacts', ContactListCreateView.as_view(), name='contact-list-create'),
    path('contacts/<int:contact_id>', ContactDetailView.as_view(), name='contact-detail'),
    path('customer/me', CustomerMeView.as_view(), name='customer-me'),
]
