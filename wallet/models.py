from django.db import models
from django.conf import settings
from price.models import CryptoCoin, CryptoPrice

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

    def create_address(self, wallet, cad, btc):

        address = os.popen(f"{settings.ELECTRUM} createnewaddress").read()

        CryptoAddress.objects.create(
            address=address,
            wallet=wallet,
            cad_due=cad,
            btc_due=btc
        )


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
        '''Electrum notify command. Returns true'''
        # TODO url = reverse(this function does some urls.py shit)
        if json.loads(os.popen(f"{settings.ELECTRUM} notify {self.address} {url}").read()) == True:
            return True
        else:
            return False










# class PriceApi(models.Model):

#     name = models.CharField(max_length=255,unique=True)
#     url = models.UrlField()












