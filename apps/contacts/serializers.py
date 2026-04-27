"""Serializers for Contact."""
from rest_framework import serializers

from .models import Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'organization')

    def validate(self, attrs):
        # Mobile + type uniqueness per org is enforced by DB constraint,
        # but provide a cleaner error message here.
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            org = request.user.organization
            contact_type = attrs.get('contact_type', Contact.TYPE_CUSTOMER)
            mobile = attrs.get('mobile')
            if mobile:
                qs = Contact.objects.filter(
                    organization=org,
                    contact_type=contact_type,
                    mobile=mobile,
                )
                if self.instance:
                    qs = qs.exclude(pk=self.instance.pk)
                if qs.exists():
                    raise serializers.ValidationError(
                        {'mobile': 'A contact with this mobile number already exists.'}
                    )
        return attrs


class ContactListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""

    class Meta:
        model = Contact
        fields = (
            'id', 'contact_type', 'name', 'email', 'mobile',
            'status', 'payment_status', 'area', 'branch_id',
            'connection_type', 'package', 'tags', 'created_at',
        )
