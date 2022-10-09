from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response

from .models import CryptoAddress, CryptoWallet
from .serializers import NewAddressSerializer
from price.models import CryptoCoin, CryptoPrice

import decimal
import json


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def vendor_request_test(request):

    if request.method != 'POST':
        return HttpResponseBadRequest

    # TODO: how to clean the data? do i treat this like a form?
    data = request.data
    wallet = get_object_or_404(CryptoWallet, vendor_key=data['api-key'])
    
    # Poduction:
    # wallet.load_wallet()
    cad = data['cad']

    price = CryptoPrice.objects.filter(coin_fk__coin_name='bitcoin').last()
    # TODO: check to make sure price is < 15 minutes ago.
    # TODO: if price is not less than 15 mins, raise error and do another API call i guess lol.

    btc = price.cad_to_btc(decimal.Decimal(cad))
    address = CryptoAddress.objects.add_request(
        wallet=wallet,
        cad_amount=cad,
        btc_amount=btc
    )

    resp = address.payment_details()

    # for thing in dir(request):
    #     print(thing)
    print(request.stream)

    serializer = NewAddressSerializer(resp)

    address.delete()

    return Response(serializer.data)




@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def notification(request):

    if request.method != 'POST':
        return HttpResponseBadRequest
    
    data = request.data

    address = get_object_or_404(CryptoAddress, address=data['address'])
    
    balance = {'unconfirmed':0, 'confirmed':decimal.Decimal(0.0)}

    print(address.confirm_full_payment(balance))
    print(address.currency_sanity_check(balance))
    # electrum notify POST request:
    # body = {
    #     "address"   : "bc1qkfcwrwva3s82j3m4uyv7zvvsgqk9kc36ggykw2", 
    #     "status"    : "3742b7c6e559d347734a4c4cdd40fded22458fd6b43f9a2f78d61a990c5ca712"},

    return HttpResponse('hihih')




