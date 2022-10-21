from django.conf import settings
from .errors import CoinGeckoError, CoinMarketCapError
from .models import CryptoPrice, CryptoCoin

from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

import decimal
import json


class PriceFetch():

    # def __init__(self, api):
    #     self.api = api



    def _coingecko(self):
        """
        API Call to CoinGecko to fetch crypto prices and save them into the database
        """
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin%2Clitecoin&vs_currencies=cad'

        parameters = {
            'ids'           :settings.COINS_LONG,
            'vs_currencies' : 'cad',
        }
        headers = {
            'Accepts': 'application/json',
        }

        session = Session()
        session.headers.update(headers)

        coin_prices = {}

        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)

            for coin in settings.COINS_LONG.split(','):
                coin_prices[coin.lower()] = decimal.Decimal(round(data[coin]['cad'], 2))


        except (ConnectionError, Timeout, TooManyRedirects) as e:
            raise e
            # TODO try a 3rd API? log this shit too 

        prices = []
        for coin, price in coin_prices.items():
            crypto_coin = CryptoCoin.objects.get(coin_name=coin)
            price_obj = CryptoPrice.objects.create(coin_fk=crypto_coin, price=price)
            prices.append(price_obj)

        return tuple(prices)



    def coingecko(self):
        prices = self._coingecko()
        if type(prices) == tuple:
            raise CoinGeckoError
        return prices





        