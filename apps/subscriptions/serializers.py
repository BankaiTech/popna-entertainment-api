from rest_framework import serializers
from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'organization')


class SubscriptionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = (
            'id', 'plan_name', 'amount', 'billing_cycle',
            'start_date', 'next_billing_date', 'status',
            'auto_renew', 'contact_id', 'created_at',
        )
