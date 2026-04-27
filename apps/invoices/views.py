"""Views for Invoices (sales, purchase, POS) + /pos aliases."""
import logging

from rest_framework import status
from rest_framework.views import APIView

from common.permissions.permissions import IsCustomer, IsOrgMember
from common.utils.pagination import StandardResultsSetPagination
from common.utils.responses import created_response, error_response, success_response

from .models import Invoice
from .serializers import InvoiceListSerializer, InvoiceSerializer
from .services import InvoiceService

logger = logging.getLogger(__name__)


class InvoiceListCreateView(APIView):
    """GET /invoices  POST /invoices"""
    permission_classes = (IsOrgMember,)

    # Optional kind override for alias routes (/pos, /products)
    _force_kind = None

    def get(self, request):
        params = dict(request.query_params)
        if self._force_kind:
            params['kind'] = self._force_kind
        qs = InvoiceService.list_invoices(request.user.organization, params)
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(InvoiceListSerializer(page, many=True).data)

    def post(self, request):
        data = request.data.copy()
        if self._force_kind and 'kind' not in data:
            data['kind'] = self._force_kind
        serializer = InvoiceSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        invoice = InvoiceService.create_invoice(
            serializer.validated_data,
            request.user.organization,
        )
        return created_response(data=InvoiceSerializer(invoice).data)


class InvoiceDetailView(APIView):
    """GET /invoices/:id  PATCH /invoices/:id  DELETE /invoices/:id"""
    permission_classes = (IsOrgMember,)

    def _get(self, invoice_id, request):
        try:
            return InvoiceService.get_invoice(invoice_id, request.user.organization)
        except Invoice.DoesNotExist:
            return None

    def get(self, request, invoice_id):
        invoice = self._get(invoice_id, request)
        if not invoice:
            return error_response('Invoice not found.', http_status=status.HTTP_404_NOT_FOUND)
        return success_response(data=InvoiceSerializer(invoice).data)

    def patch(self, request, invoice_id):
        invoice = self._get(invoice_id, request)
        if not invoice:
            return error_response('Invoice not found.', http_status=status.HTTP_404_NOT_FOUND)
        serializer = InvoiceSerializer(invoice, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        invoice = InvoiceService.update_invoice(invoice, serializer.validated_data)
        return success_response(data=InvoiceSerializer(invoice).data)

    def delete(self, request, invoice_id):
        invoice = self._get(invoice_id, request)
        if not invoice:
            return error_response('Invoice not found.', http_status=status.HTTP_404_NOT_FOUND)
        InvoiceService.void_or_delete(invoice)
        return success_response(message='Invoice voided or deleted.')


class CustomerInvoicesView(APIView):
    """GET /customer/invoices — customer portal: own invoices."""
    permission_classes = (IsCustomer,)

    def get(self, request):
        qs = Invoice.objects.filter(
            organization_id=request.user.organization_id,
            contact_id=request.user.contact.id,
        )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(InvoiceListSerializer(page, many=True).data)


# POS alias views — force kind='pos'
class POSListCreateView(InvoiceListCreateView):
    _force_kind = Invoice.KIND_POS


class POSDetailView(InvoiceDetailView):
    pass
