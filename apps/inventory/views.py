"""Views for Inventory (unified catalog + product/plan aliases)."""
import logging

from rest_framework import status
from rest_framework.views import APIView

from common.permissions.permissions import IsOrgMember
from common.utils.pagination import StandardResultsSetPagination
from common.utils.responses import created_response, error_response, success_response

from .models import Inventory
from .serializers import InventoryListSerializer, InventorySerializer
from .services import InventoryService

logger = logging.getLogger(__name__)


class InventoryListCreateView(APIView):
    """GET /inventory  POST /inventory"""
    permission_classes = (IsOrgMember,)

    def get(self, request):
        qs = InventoryService.list_items(request.user.organization, request.query_params)
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(InventoryListSerializer(page, many=True).data)

    def post(self, request):
        serializer = InventorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = InventoryService.create_item(
            serializer.validated_data,
            request.user.organization,
        )
        return created_response(data=InventorySerializer(item).data)


class InventoryDetailView(APIView):
    """GET /inventory/:id  PATCH /inventory/:id  DELETE /inventory/:id"""
    permission_classes = (IsOrgMember,)

    def _get_item(self, item_id, request):
        try:
            return InventoryService.get_item(item_id, request.user.organization)
        except Inventory.DoesNotExist:
            return None

    def get(self, request, item_id):
        item = self._get_item(item_id, request)
        if not item:
            return error_response('Item not found.', http_status=status.HTTP_404_NOT_FOUND)
        return success_response(data=InventorySerializer(item).data)

    def patch(self, request, item_id):
        item = self._get_item(item_id, request)
        if not item:
            return error_response('Item not found.', http_status=status.HTTP_404_NOT_FOUND)
        serializer = InventorySerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        item = InventoryService.update_item(item, serializer.validated_data)
        return success_response(data=InventorySerializer(item).data)

    def delete(self, request, item_id):
        item = self._get_item(item_id, request)
        if not item:
            return error_response('Item not found.', http_status=status.HTTP_404_NOT_FOUND)
        InventoryService.deactivate_item(item)
        return success_response(message='Item deactivated.')


class InventoryLowStockView(APIView):
    """GET /inventory/low-stock"""
    permission_classes = (IsOrgMember,)

    def get(self, request):
        qs = InventoryService.low_stock_items(request.user.organization)
        return success_response(data=InventoryListSerializer(qs, many=True).data)


class InventoryBarcodeView(APIView):
    """GET /inventory/barcode/:barcode"""
    permission_classes = (IsOrgMember,)

    def get(self, request, barcode):
        try:
            item = InventoryService.get_by_barcode(barcode, request.user.organization)
        except Inventory.DoesNotExist:
            return error_response('Item not found.', http_status=status.HTTP_404_NOT_FOUND)
        return success_response(data=InventorySerializer(item).data)
