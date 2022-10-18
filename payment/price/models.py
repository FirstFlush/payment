from django.db import models
from django.conf import settings 

from payment.error.errors import PriceFetchApiFailure

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

    def get_latest_price(self, coin):
        '''Grabs the latest price'''
            
        t = datetime.now()
        time_threshold = t - timedelta(minutes=15)

        latest_price = CryptoPrice.objects.filter(coin_fk=coin, date_created__gt=time_threshold).last()

        if latest_price == None:
            # log and also maybe put in a 3rd api call here?
            print('[NO PRICE] Gotta fetch a new price!! Making API Call')
            CryptoPrice.objects.coingecko()
            latest_price = CryptoPrice.objects.filter(coin_fk=coin, date_created__gt=time_threshold).last()

        else:
            print('[PRICE FOUND] No need to fetch a new price')

        return latest_price


    def coingecko(self):
        '''
        API Call to CoinGecko to fetch crypto prices and save them into the database
        '''

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

        print(coin_prices)

        for coin, price in coin_prices.items():
            crypto_coin = CryptoCoin.objects.get(coin_name=coin)
            CryptoPrice.objects.create(coin_fk=crypto_coin, price=price)

        return


    def coinmarketcap(request):
        '''
        Backup API with CoinMarketCap in case the CoinGecko API fails
        '''

        url = ' https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

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

            coin_prices['bitcoin'] = decimal.Decimal(round(data['data']['BTC']['quote']['CAD']['price'], 2))
            coin_prices['litecoin'] = decimal.Decimal(round(data['data']['LTC']['quote']['CAD']['price'], 2))

        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
            

        print('-'*30)
        print(coin_prices)
        print('-'*30)

        for coin, price in coin_prices.items():
            crypto_coin = CryptoCoin.objects.get(coin_name=coin)
            CryptoPrice.objects.create(coin_fk=crypto_coin, price=price)

        return



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
        #TODO test
        cad = self.price * btc
        return cad


    def check_time(self):

        # TODO needs work lolol
        # t = datetime.utcnow()
        time_threshold = datetime.now() - timedelta(minutes=15)
        if self.date_created > time_threshold:
            print('good?')
        else:
            print('bad i think')


    def __str__(self):
        time_str = self.date_created.strftime('%B %d, %Y, %I:%M %p')
        return f"{self.coin_fk} - ${self.price} - {time_str}"


    def round_digits(self):
        '''
        Checks which coin we are dealing with, then decides how many digits to round
        '''
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






class PriceApiFailureManager(models.Manager):

    def fail(e, failed_api):

        error_str = str(type(e))[:50]

        raise PriceFetchApiFailure

        PriceApiFailure.objects.create(
            failed_api=failed_api,
            error=error_str
        )



class PriceApiFailure(models.Model):

    FAILURE_CHOICES = (
        ('coingecko', 'coingecko.com'),
        ('coinmarketcap', 'coinmarketcap.com'),
    )

    failed_api      = models.CharField(max_length=50, choices=FAILURE_CHOICES)
    error           = models.CharField(max_length=60)
    date_created    = models.DateTimeField(auto_now_add=True)

    objects = PriceApiFailureManager()

    class Meta:
        verbose_name = 'Price API Failure'
        verbose_name_plural = 'Price API Failures'

