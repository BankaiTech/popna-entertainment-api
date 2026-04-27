from django.urls import path
from .views import CustomerSubscriptionsView, SubscriptionDetailView, SubscriptionListCreateView

urlpatterns = [
    path('subscriptions', SubscriptionListCreateView.as_view(), name='subscription-list-create'),
    path('subscriptions/<int:sub_id>', SubscriptionDetailView.as_view(), name='subscription-detail'),
    path('customer/subscriptions', CustomerSubscriptionsView.as_view(), name='customer-subscriptions'),
]
