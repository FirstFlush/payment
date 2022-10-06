from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions

from .models import CryptoAddress, CryptoWallet
from price.models import CryptoCoin, CryptoPrice

import decimal


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def notification(request):

    if request.method != 'POST':
        return HttpResponseBadRequest
    
    data = request.data

    address = get_object_or_404(CryptoAddress, address=data['address'])
    
    balance = {'unconfirmed':0, 'confirmed':decimal.Decimal(0.0)}

    print(address.confirm_full_payment(balance))
    print(address.exchange_sanity_check(balance))
    # electrum notify POST request:
    # body = {
    #     "address"   : "bc1qkfcwrwva3s82j3m4uyv7zvvsgqk9kc36ggykw2", 
    #     "status"    : "3742b7c6e559d347734a4c4cdd40fded22458fd6b43f9a2f78d61a990c5ca712"},

    return HttpResponse('hihih')



@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def get_price_test(request):

    # data = request.data
    # print(request.GET['coin'])
    # CryptoPrice.objects.coingecko()
    CryptoPrice.objects.coinmarketcap()

    return HttpResponse('hohoho')



