"""Views for Documents."""
import logging
from rest_framework import status
from rest_framework.views import APIView
from common.permissions.permissions import IsOrgMember
from common.utils.pagination import StandardResultsSetPagination
from common.utils.responses import created_response, error_response, success_response
from .models import Document
from .serializers import DocumentListSerializer, DocumentSerializer
from .services import DocumentService

logger = logging.getLogger(__name__)


class DocumentListCreateView(APIView):
    """GET /documents  POST /documents"""
    permission_classes = (IsOrgMember,)

    def get(self, request):
        qs = DocumentService.list_documents(request.user.organization, request.query_params)
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(DocumentListSerializer(page, many=True).data)

    def post(self, request):
        serializer = DocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doc = DocumentService.create_document(serializer.validated_data, request.user.organization)
        return created_response(data=DocumentSerializer(doc).data)


class DocumentDetailView(APIView):
    """GET /documents/:id  PATCH /documents/:id  DELETE /documents/:id"""
    permission_classes = (IsOrgMember,)

    def _get(self, doc_id, request):
        try:
            return DocumentService.get_document(doc_id, request.user.organization)
        except Document.DoesNotExist:
            return None

    def get(self, request, doc_id):
        doc = self._get(doc_id, request)
        if not doc:
            return error_response('Document not found.', http_status=status.HTTP_404_NOT_FOUND)
        return success_response(data=DocumentSerializer(doc).data)

    def patch(self, request, doc_id):
        doc = self._get(doc_id, request)
        if not doc:
            return error_response('Document not found.', http_status=status.HTTP_404_NOT_FOUND)
        serializer = DocumentSerializer(doc, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        doc = DocumentService.update_document(doc, serializer.validated_data)
        return success_response(data=DocumentSerializer(doc).data)

    def delete(self, request, doc_id):
        doc = self._get(doc_id, request)
        if not doc:
            return error_response('Document not found.', http_status=status.HTTP_404_NOT_FOUND)
        DocumentService.delete_document(doc)
        return success_response(message='Document deleted.')
