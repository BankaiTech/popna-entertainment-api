from django.urls import path
from .views import ActivityDetailView, ActivityListCreateView, CustomerComplaintsView

urlpatterns = [
    path('activities', ActivityListCreateView.as_view(), name='activity-list-create'),
    path('activities/<int:activity_id>', ActivityDetailView.as_view(), name='activity-detail'),
    path('customer/complaints', CustomerComplaintsView.as_view(), name='customer-complaints'),
]
