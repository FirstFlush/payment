from rest_framework import serializers
from .models import PaymentRequest, Payment


class PayRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentRequest
        fields = '__all__'
        depth = 1
        # exclude = ['btc_due']


class PaymentSerializer(serializers.ModelSerializer):

    address = serializers.CharField(source='address_id.address')
    exg_rate = serializers.CharField(source='price_id.price')
    # vendor_url = serializers.CharField(source='address_id.wallet_id.vendor_url')

    class Meta:
        model = Payment
        fields = [
            'address',
            'exg_rate',
            'btc_confirmed',
            'cad_exchange',
            'is_problem',
            'date_created',
            # 'vendor_url',
        ]
