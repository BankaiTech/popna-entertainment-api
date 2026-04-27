from rest_framework import serializers
from .models import OrgSettings


class OrgSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgSettings
        exclude = ('id', 'organization')
        read_only_fields = ('updated_at',)


class CustomFieldSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgSettings
        fields = ('custom_field_schema',)


class WebsiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgSettings
        fields = ('website',)


class BranchesSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgSettings
        fields = ('branches',)
