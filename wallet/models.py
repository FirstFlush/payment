from django.db import models
from django.conf import settings
from price.models import CryptoCoin, CryptoPrice
from account.models import Account

import json
import decimal
import os



def decimalize(dictionary):
    '''
    dict -> dict

    Used to convert number strings like '0.0035132' 
    in electrum CLI responses into dictionaries.
    '''
    for key, value in dictionary.items():
        try:
            dictionary[key] = decimal.Decimal(value)
        except decimal.InvalidOperation:
            pass

    return dictionary



class CryptoWallet(models.Model):

    account_id  = models.ForeignKey(to=Account, on_delete=models.CASCADE)
    wallet_name = models.CharField(max_length=255, unique=True)
    mpk         = models.CharField(max_length=255, unique=True)
    slug        = models.SlugField(max_length=255, unique=True)


    def path(self):
        return f"{settings.WALLET_DIR}/{self.wallet_name}"

    def mpk_short(self):
        return f"{self.mpk[:8]}....{self.mpk[-4:]}"

    def __str__(self):
        return self.wallet_name



class CryptoAddressManager(models.Manager):


    def new_address(self, wallet, cad_amount, btc_amount):

        request = os.popen(f"{settings.ELECTRUM} add_request {btc_amount}").read()
        request = json.loads(request)

        btc_address = request['address']

        CryptoAddress.objects.create(
            address=btc_address,
            wallet=wallet,
            cad_due=cad_amount,
            btc_due=btc_amount
        )
# electrum output:
# {
#     "URI": "bitcoin:bc1q0jvf6pdsls8gcjm02yed3n6k6vzfywuvsfs75u?amount=0.00027921&time=1664956697&exp=3600",
#     "address": "bc1q0jvf6pdsls8gcjm02yed3n6k6vzfywuvsfs75u",
#     "amount_BTC": "0.00027921",
#     "amount_sat": 27921,
#     "expiration": 3600,
#     "is_lightning": false,
#     "message": "",
#     "status": 0,
#     "status_str": "Expires in about 1 hour",
#     "timestamp": 1664956697
# }



class CryptoAddress(models.Model):

    wallet_id       = models.ForeignKey(to=CryptoWallet, on_delete=models.CASCADE, null=True, blank=True)
    address         = models.CharField(max_length=255, unique=True)
    btc_due         = models.DecimalField(decimal_places=7, max_digits=10)
    cad_due         = models.DecimalField(decimal_places=2, max_digits=10)
    btc_paid        = models.DecimalField(decimal_places=7, max_digits=10, default=0)
    is_paid         = models.BooleanField(default=False)
    date_created    = models.DateTimeField(auto_now_add=True)

    objects = CryptoAddressManager()


    def get_balance(self):
        '''
        Checks the address' balance. Returns a dict of decimals:
        {
            'confirmed' : 0.0034423,
            'unconfirmed' : 0,
        }
        '''
        bal = os.popen(f"{settings.ELECTRUM} getaddressbalance {self.address}").read()
        bal = decimalize(json.loads(bal))

        return bal


    def list_addresses(self):
        '''Returns a list of all addresses in the wallet'''
        addys = os.popen(f"{settings.ELECTRUM} listaddresses").read()
        addys = decimalize(json.loads(addys))
        return addys


    def notify(self, url=str):
        '''Electrum notify command. Returns boolean'''
        # TODO url = reverse(this function does some urls.py shit)
        if json.loads(os.popen(f"{settings.ELECTRUM} notify {self.address} {url}").read()) == True:
            return True
        else:
            return False








# class PriceApi(models.Model):

#     name = models.CharField(max_length=255,unique=True)
#     url = models.UrlField()












