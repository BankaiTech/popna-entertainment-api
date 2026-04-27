"""Serializers for Activity."""
from rest_framework import serializers

from .models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'organization')

    def validate_kind(self, value):
        valid = [k[0] for k in Activity.KIND_CHOICES]
        if value not in valid:
            raise serializers.ValidationError(f'kind must be one of: {valid}')
        return value


class ActivityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = (
            'id', 'kind', 'status', 'priority', 'assigned_to',
            'contact_id', 'created_at', 'updated_at',
        )
