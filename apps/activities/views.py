"""Views for Activities."""
import logging

from rest_framework import status
from rest_framework.views import APIView

from common.permissions.permissions import IsCustomer, IsOrgMember
from common.utils.pagination import StandardResultsSetPagination
from common.utils.responses import created_response, error_response, success_response

from .models import Activity
from .serializers import ActivityListSerializer, ActivitySerializer
from .services import ActivityService

logger = logging.getLogger(__name__)


class ActivityListCreateView(APIView):
    """GET /activities  POST /activities"""
    permission_classes = (IsOrgMember,)

    def get(self, request):
        qs = ActivityService.list_activities(request.user.organization, request.query_params)
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(ActivityListSerializer(page, many=True).data)

    def post(self, request):
        serializer = ActivitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        activity = ActivityService.create_activity(
            serializer.validated_data,
            request.user.organization,
        )
        return created_response(data=ActivitySerializer(activity).data)


class ActivityDetailView(APIView):
    """GET /activities/:id  PATCH /activities/:id  DELETE /activities/:id"""
    permission_classes = (IsOrgMember,)

    def _get(self, activity_id, request):
        try:
            return ActivityService.get_activity(activity_id, request.user.organization)
        except Activity.DoesNotExist:
            return None

    def get(self, request, activity_id):
        activity = self._get(activity_id, request)
        if not activity:
            return error_response('Activity not found.', http_status=status.HTTP_404_NOT_FOUND)
        return success_response(data=ActivitySerializer(activity).data)

    def patch(self, request, activity_id):
        activity = self._get(activity_id, request)
        if not activity:
            return error_response('Activity not found.', http_status=status.HTTP_404_NOT_FOUND)
        serializer = ActivitySerializer(activity, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        activity = ActivityService.update_activity(activity, serializer.validated_data)
        return success_response(data=ActivitySerializer(activity).data)

    def delete(self, request, activity_id):
        activity = self._get(activity_id, request)
        if not activity:
            return error_response('Activity not found.', http_status=status.HTTP_404_NOT_FOUND)
        ActivityService.delete_activity(activity)
        return success_response(message='Activity deleted.')


class CustomerComplaintsView(APIView):
    """GET /customer/complaints — customer portal: own complaints."""
    permission_classes = (IsCustomer,)

    def get(self, request):
        qs = Activity.objects.filter(
            organization_id=request.user.organization_id,
            kind=Activity.KIND_COMPLAINT,
            contact_id=request.user.contact.id,
        )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(ActivityListSerializer(page, many=True).data)
