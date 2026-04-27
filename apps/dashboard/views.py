"""Dashboard & reporting views."""
import logging
from django.db.models import Count, Sum, Q
from django.utils import timezone
from rest_framework.views import APIView
from common.permissions.permissions import IsCustomer, IsOrgMember
from common.utils.responses import success_response

logger = logging.getLogger(__name__)


class DashboardStatsView(APIView):
    """GET /dashboard/stats — admin KPIs."""
    permission_classes = (IsOrgMember,)

    def get(self, request):
        from apps.contacts.models import Contact
        from apps.activities.models import Activity
        from apps.invoices.models import Invoice
        from apps.subscriptions.models import Subscription

        org = request.user.organization

        # Contacts
        total_customers = Contact.objects.filter(
            organization=org, contact_type='customer'
        ).count()
        active_customers = Contact.objects.filter(
            organization=org, contact_type='customer', status='Active'
        ).count()

        # Activities by kind
        activity_counts = (
            Activity.objects.filter(organization=org)
            .values('kind')
            .annotate(count=Count('id'))
        )
        activities_by_kind = {row['kind']: row['count'] for row in activity_counts}

        # Invoices
        invoice_stats = Invoice.objects.filter(organization=org).aggregate(
            total_sales=Sum('total_amount', filter=Q(kind='sales')),
            total_purchase=Sum('total_amount', filter=Q(kind='purchase')),
            total_pos=Sum('total_amount', filter=Q(kind='pos')),
            paid_count=Count('id', filter=Q(status='paid')),
            overdue_count=Count('id', filter=Q(status='overdue')),
        )

        # Subscriptions
        active_subs = Subscription.objects.filter(organization=org, status='active').count()
        due_subs = Subscription.objects.filter(
            organization=org,
            status='active',
            next_billing_date__lte=timezone.now().date(),
        ).count()

        data = {
            'contacts': {
                'total_customers': total_customers,
                'active_customers': active_customers,
            },
            'activities': activities_by_kind,
            'invoices': {
                'total_sales': invoice_stats['total_sales'] or 0,
                'total_purchase': invoice_stats['total_purchase'] or 0,
                'total_pos': invoice_stats['total_pos'] or 0,
                'paid_count': invoice_stats['paid_count'],
                'overdue_count': invoice_stats['overdue_count'],
            },
            'subscriptions': {
                'active': active_subs,
                'due': due_subs,
            },
        }

        return success_response(data=data)


class DashboardLastCustomersView(APIView):
    """GET /dashboard/last-customers — last N customers."""
    permission_classes = (IsOrgMember,)

    def get(self, request):
        from apps.contacts.models import Contact
        from apps.contacts.serializers import ContactListSerializer

        n = int(request.query_params.get('n', 10))
        customers = Contact.objects.filter(
            organization=request.user.organization,
            contact_type='customer',
        ).order_by('-created_at')[:n]

        return success_response(data=ContactListSerializer(customers, many=True).data)


class CustomerDashboardView(APIView):
    """GET /customer/dashboard — customer portal summary."""
    permission_classes = (IsCustomer,)

    def get(self, request):
        from apps.subscriptions.models import Subscription
        from apps.subscriptions.serializers import SubscriptionSerializer
        from apps.invoices.models import Invoice
        from apps.invoices.serializers import InvoiceListSerializer

        contact = request.user.contact

        # Active subscription
        active_sub = Subscription.objects.filter(
            contact=contact,
            status='active',
        ).order_by('-created_at').first()

        # Recent invoices
        recent_invoices = Invoice.objects.filter(
            contact=contact,
        ).order_by('-created_at')[:5]

        data = {
            'subscription': SubscriptionSerializer(active_sub).data if active_sub else None,
            'recent_invoices': InvoiceListSerializer(recent_invoices, many=True).data,
            'next_due': active_sub.next_billing_date if active_sub else None,
        }

        return success_response(data=data)
