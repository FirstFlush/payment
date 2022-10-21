from logging import NOTSET
from django.db import models
from django.conf import settings 

from .errors import CoinGeckoError, CoinMarketCapError

from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from datetime import datetime, timedelta
import json
import decimal

# import logging


class CryptoCoin(models.Model):

    coin_name       = models.CharField(max_length=50, unique=True)
    coin_name_short = models.CharField(max_length=10, unique=True)
    
    class Meta:
        verbose_name = 'Crypto Coin'
        verbose_name_plural = 'Crypto Coins'


    def __str__(self):
        return self.coin_name_short.upper()



class CryptoPriceManager(models.Manager):


    def delete_old(self):
        """Deletes all the prices that are older than (x) days,
        as defined in settings.py
        """
        time_threshold = datetime.utcnow() - timedelta(days=settings.DELETE_PRICE_DAYS)
        old_prices = CryptoPrice.objects.filter(date_created__date__lt=time_threshold)
        old_prices.delete()


    def _coingecko(self) -> tuple:
        """API Call to CoinGecko to fetch crypto 
        prices and save them into the database.
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
        except (ConnectionError, Timeout, TooManyRedirects):
            raise CoinGeckoError
        else:
            for coin in settings.COINS_LONG.split(','):
                coin_prices[coin.lower()] = decimal.Decimal(round(data[coin]['cad'], 2))

        prices = []
        for coin, price in coin_prices.items():
            crypto_coin = CryptoCoin.objects.get(coin_name=coin)
            price_obj = CryptoPrice.objects.create(coin_fk=crypto_coin, price=price)
            prices.append(price_obj)

        return tuple(prices)


    def _coinmarketcap(request) -> tuple:
        """Backup API with CoinMarketCap in case 
        the CoinGecko API fails
        """

        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

        parameters = {
            'convert':'CAD',
            'symbol': settings.COINS_SHORT,
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': settings.COINMARKETCAP_API_KEY,
        }

        session = Session()
        session.headers.update(headers)

        coin_prices = {}

        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
        except (ConnectionError, Timeout, TooManyRedirects):
            raise CoinMarketCapError
        else:
            coin_prices['bitcoin'] = decimal.Decimal(round(data['data']['BTC']['quote']['CAD']['price'], 2))
            coin_prices['litecoin'] = decimal.Decimal(round(data['data']['LTC']['quote']['CAD']['price'], 2))

        prices = []
        for coin, price in coin_prices.items():
            crypto_coin = CryptoCoin.objects.get(coin_name=coin)
            price_obj = CryptoPrice.objects.create(coin_fk=crypto_coin, price=price)
            prices.append(price_obj)

        return tuple(prices)


    def coingecko(self):
        prices = self._coingecko()
        if type(prices) != tuple:
            raise CoinGeckoError
        return prices


    def coinmarketcap(self):
        prices = self._coinmarketcap()
        if type(prices) != tuple:
            raise CoinMarketCapError
        return prices



class CryptoPrice(models.Model):
    '''1 BTC = self.price'''

    coin_fk         = models.ForeignKey(to=CryptoCoin, on_delete=models.CASCADE)
    price           = models.DecimalField(decimal_places=2, max_digits=20)
    date_created    = models.DateTimeField(auto_now_add=True)

    objects = CryptoPriceManager()


    def cad_to_btc(self, cad):
        #TODO test
        btc = cad / self.price
        return btc


    def btc_to_cad(self, btc):
        cad = self.price * btc
        return cad


    def check_time(self):
        """Returns True if the time was fetched within (x) minutes, as defined in settings.py"""
        time_threshold = datetime.utcnow() - timedelta(minutes=settings.TIME_CHECK)
        if self.date_created.replace(tzinfo=None) > time_threshold:
            return True
        else:
            return False


    def __str__(self):
        time_str = self.date_created.strftime('%B %d, %Y, %I:%M %p')
        return f"{self.coin_fk} - ${self.price} - {time_str}"


    def round_digits(self):
        """
        Returns integer for # of digits the price will be rounded to.
        """
        coins = {
            'bitcoin'   : 6,
            'litecoin'  : 3,
        }
        try:
            for coin in coins.keys():
                if self.coin_fk.coin_name == coin:
                   digits = coins.get(coin)
        except:
            digits = 6

        return digits



class PriceApiFailure(models.Model):

    error           = models.CharField(max_length=255)
    date_created    = models.DateTimeField(auto_now_add=True)
    notes           = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Price API Failure'
        verbose_name_plural = 'Price API Failures'

