from django.shortcuts import render
from .models import CryptoPrice#, PriceApiFailure
# Create your views here.


def get_price():
    return
#     '''
#     Makes first API call to CoinGecko and if that fails it makes an API call to CoinMarketCap. If either API call fails, a failure is recorded in the database.
#     '''
    
#     try:
#         CryptoPrice.objects.fetch_prices()
#     except Exception as e:
#         error_str = str(type(e))[:50]
#         CryptoApiFailure.objects.create(failed_api='api_one', error=error_str)

#         try:
#             CryptoPrice.objects.fetch_prices_backup()
#         except Exception as e:
#             error_str = str(type(e))[:50]
#             CryptoApiFailure.objects.create(failed_api='api_two', error=error_str)

#     return