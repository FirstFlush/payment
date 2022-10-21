from rest_framework import serializers
from .models import CryptoPrice, PriceApiFailure


# class CurrentPriceSerializer(serializers.Serializer):
#     pass


class PriceApiFailureSerializer(serializers.ModelSerializer):

    class Meta:
        model = PriceApiFailure
        fields = '__all__'