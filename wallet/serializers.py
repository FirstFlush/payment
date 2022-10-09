from rest_framework import serializers



class NewAddressSerializer(serializers.Serializer):

    address = serializers.CharField(max_length=255)
    btc_due = serializers.DecimalField(max_digits=20, decimal_places=7)
    qr_code = serializers.CharField()
