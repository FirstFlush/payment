from rest_framework import serializers
from .models import PaymentRequest, Payment


class PayRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentRequest
        fields = '__all__'
        depth = 1
        # exclude = ['btc_due']