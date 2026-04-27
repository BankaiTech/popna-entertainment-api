"""Views for Subscriptions."""
import logging
from rest_framework import status
from rest_framework.views import APIView
from common.permissions.permissions import IsCustomer, IsOrgMember
from common.utils.pagination import StandardResultsSetPagination
from common.utils.responses import created_response, error_response, success_response
from .models import Subscription
from .serializers import SubscriptionListSerializer, SubscriptionSerializer
from .services import SubscriptionService

logger = logging.getLogger(__name__)


class SubscriptionListCreateView(APIView):
    """GET /subscriptions  POST /subscriptions"""
    permission_classes = (IsOrgMember,)

    def get(self, request):
        qs = SubscriptionService.list_subscriptions(request.user.organization, request.query_params)
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(SubscriptionListSerializer(page, many=True).data)

    def post(self, request):
        serializer = SubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sub = SubscriptionService.create_subscription(
            serializer.validated_data, request.user.organization
        )
        return created_response(data=SubscriptionSerializer(sub).data)


class SubscriptionDetailView(APIView):
    """GET /subscriptions/:id  PATCH /subscriptions/:id  DELETE /subscriptions/:id"""
    permission_classes = (IsOrgMember,)

    def _get(self, sub_id, request):
        try:
            return SubscriptionService.get_subscription(sub_id, request.user.organization)
        except Subscription.DoesNotExist:
            return None

    def get(self, request, sub_id):
        sub = self._get(sub_id, request)
        if not sub:
            return error_response('Subscription not found.', http_status=status.HTTP_404_NOT_FOUND)
        return success_response(data=SubscriptionSerializer(sub).data)

    def patch(self, request, sub_id):
        sub = self._get(sub_id, request)
        if not sub:
            return error_response('Subscription not found.', http_status=status.HTTP_404_NOT_FOUND)
        serializer = SubscriptionSerializer(sub, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        sub = SubscriptionService.update_subscription(sub, serializer.validated_data)
        return success_response(data=SubscriptionSerializer(sub).data)

    def delete(self, request, sub_id):
        sub = self._get(sub_id, request)
        if not sub:
            return error_response('Subscription not found.', http_status=status.HTTP_404_NOT_FOUND)
        SubscriptionService.cancel_subscription(sub)
        return success_response(message='Subscription cancelled.')


class CustomerSubscriptionsView(APIView):
    """GET /customer/subscriptions — customer portal."""
    permission_classes = (IsCustomer,)

    def get(self, request):
        qs = Subscription.objects.filter(
            organization_id=request.user.organization_id,
            contact_id=request.user.contact.id,
        )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(SubscriptionListSerializer(page, many=True).data)
