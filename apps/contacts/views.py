"""Views for Contacts (customers, suppliers, vendors)."""
import logging

from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView

from common.permissions.permissions import IsCustomer, IsOrgMember
from common.utils.pagination import StandardResultsSetPagination
from common.utils.responses import created_response, error_response, success_response

from .models import Contact
from .serializers import ContactListSerializer, ContactSerializer
from .services import ContactService

logger = logging.getLogger(__name__)


class ContactListCreateView(APIView):
    """GET /contacts  POST /contacts"""
    permission_classes = (IsOrgMember,)

    def get(self, request):
        qs = Contact.objects.filter(organization=request.user.organization)

        # Filtering
        contact_type = request.query_params.get('type')
        payment_status = request.query_params.get('paymentStatus')
        cust_status = request.query_params.get('status')
        search = request.query_params.get('search')
        branch_id = request.query_params.get('branch_id')

        if contact_type:
            qs = qs.filter(contact_type=contact_type)
        if payment_status:
            qs = qs.filter(payment_status=payment_status)
        if cust_status:
            qs = qs.filter(status=cust_status)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(mobile__icontains=search)
                | Q(email__icontains=search)
                | Q(area__icontains=search)
            )

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = ContactListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ContactSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        contact = ContactService.create_contact(
            serializer.validated_data,
            request.user.organization,
        )
        return created_response(data=ContactSerializer(contact).data)


class ContactDetailView(APIView):
    """GET /contacts/:id  PATCH /contacts/:id  DELETE /contacts/:id"""
    permission_classes = (IsOrgMember,)

    def _get_contact(self, contact_id, request):
        try:
            return ContactService.get_contact(contact_id, request.user.organization)
        except Contact.DoesNotExist:
            return None

    def get(self, request, contact_id):
        contact = self._get_contact(contact_id, request)
        if not contact:
            return error_response('Contact not found.', http_status=status.HTTP_404_NOT_FOUND)
        return success_response(data=ContactSerializer(contact).data)

    def patch(self, request, contact_id):
        contact = self._get_contact(contact_id, request)
        if not contact:
            return error_response('Contact not found.', http_status=status.HTTP_404_NOT_FOUND)
        serializer = ContactSerializer(
            contact, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        contact = ContactService.update_contact(contact, serializer.validated_data)
        return success_response(data=ContactSerializer(contact).data)

    def delete(self, request, contact_id):
        contact = self._get_contact(contact_id, request)
        if not contact:
            return error_response('Contact not found.', http_status=status.HTTP_404_NOT_FOUND)
        ContactService.delete_contact(contact)
        return success_response(message='Contact deleted.')


class CustomerMeView(APIView):
    """GET /customer/me — customer portal: own profile."""
    permission_classes = (IsCustomer,)

    def get(self, request):
        serializer = ContactSerializer(request.user.contact)
        return success_response(data=serializer.data)
