from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'organization')


class DocumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = (
            'id', 'kind', 'document_number', 'status', 'total_amount',
            'contact_id', 'vendor_id', 'created_at',
        )
