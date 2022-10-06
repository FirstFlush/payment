from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions

from .models import CryptoPrice#, PriceApiFailure



@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def get_price_test(request):

    CryptoPrice.objects.coingecko()
    # CryptoPrice.objects.coinmarketcap()

    return HttpResponse('hohoho')

