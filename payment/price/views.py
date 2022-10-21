from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response

from payment.price.errors import CoinGeckoError, CoinMarketCapError

from .models import CryptoPrice, PriceApiFailure
from .classes import PriceFetch
from .serializers import PriceApiFailureSerializer



class CurrentPriceView(APIView):
    #is this view even necessary? lol
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):

        prices = CryptoPrice.objects.all()
        btc_current = prices.filter(coin_fk__coin_name='bitcoin').last()
        ltc_current = prices.filter(coin_fk__coin_name='litecoin').last()

        response = {
            'btc'       : btc_current.price,
            'ltc'       : ltc_current.price,
            'datetime'  : btc_current.date_created,
        }

        return Response(response)


class PriceApiFailureView(APIView):
    """View all reported API failures."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
   
    def get(self, request, *args, **kwargs):
        
        failures = PriceApiFailure.objects.all()
        serializer = PriceApiFailureSerializer(failures, many=True)

        return Response(serializer.data)



@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def get_price_test(request):

    prices = 'ok whatever man'

    try:
        CryptoPrice.objects.coingecko()
    except CoinGeckoError as e:
        error = e.__class__.__name__
        PriceApiFailure.objects.create(error=error)

        try:
            CryptoPrice.objects.coinmarketcap()
        except CoinMarketCapError as e:
            error = e.__class__.__name__
            PriceApiFailure.objects.create(error=error)

    return HttpResponse(prices)

