from rest_framework import serializers
from .models import PaymentRequest, Payment



class TestSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=255)
    amount = serializers.DecimalField(decimal_places=7, max_digits=10)



class NewRequestSerializer(serializers.Serializer):

    cad = serializers.DecimalField(decimal_places=2, max_digits=10)
    # hash = serializers.CharField(max_length=255)


class PayRequestSerializer(serializers.ModelSerializer):

    address = serializers.CharField(source='address_id.address')
    coin = serializers.CharField(source='address_id.wallet_id.coin_id.coin_name_short')

    class Meta:
        model = PaymentRequest
        fields = [
            'address',
            'btc_due',
            'coin',
        ]

        # depth = 1
        # exclude = ['btc_due']


class NotificationSerializer(serializers.Serializer):
    address         = serializers.CharField(max_length=255)
    status          = serializers.CharField(max_length=255) #TXID
    # btc_unconfirmed = serializers.DecimalField(decimal_places=7, max_digits=10, default=0)
    # btc_confirmed   = serializers.DecimalField(decimal_places=7, max_digits=10, default=0)




class PaymentSerializer(serializers.ModelSerializer):

    address = serializers.CharField(source='address_id.address')
    # exg_rate = serializers.CharField(source='price_id.price')
    # vendor_url = serializers.CharField(source='address_id.wallet_id.vendor_url')

    class Meta:
        model = Payment
        fields = [
            'address',
            'btc_confirmed',
            'cad_exchange',
            'status',
            'date_created',
        ]
