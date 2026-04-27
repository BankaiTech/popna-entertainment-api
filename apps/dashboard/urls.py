from django.urls import path
from .views import CustomerDashboardView, DashboardLastCustomersView, DashboardStatsView

urlpatterns = [
    path('dashboard/stats', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/last-customers', DashboardLastCustomersView.as_view(), name='dashboard-last-customers'),
    path('customer/dashboard', CustomerDashboardView.as_view(), name='customer-dashboard'),
]
