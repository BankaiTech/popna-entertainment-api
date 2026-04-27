from django.urls import path
from .views import AuditLogListView, SMSLogListView, SMSSendView

urlpatterns = [
    path('audit-log', AuditLogListView.as_view(), name='audit-log-list'),
    path('sms-logs', SMSLogListView.as_view(), name='sms-logs'),
    path('sms/send', SMSSendView.as_view(), name='sms-send'),
]
