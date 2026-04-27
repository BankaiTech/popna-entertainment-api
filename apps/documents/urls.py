from django.urls import path
from .views import DocumentDetailView, DocumentListCreateView

urlpatterns = [
    path('documents', DocumentListCreateView.as_view(), name='document-list-create'),
    path('documents/<int:doc_id>', DocumentDetailView.as_view(), name='document-detail'),
]
