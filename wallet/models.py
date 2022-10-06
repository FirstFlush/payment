from django.db import models
from django.conf import settings
from price.models import CryptoCoin, CryptoPrice
from account.models import Account

import json
import decimal
import os
import qrcode
import qrcode.image.svg
from math import isclose


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
        file_name = self.slug.replace('-','_')

        return f"{settings.WALLET_DIR}/{file_name}"

    def mpk_short(self):
        return f"{self.mpk[:8]}....{self.mpk[-4:]}"

    def __str__(self):
        return self.wallet_name




class CryptoAddressManager(models.Manager):

    def add_request(self, wallet, cad_amount, btc_amount):

        # request = os.popen(f"{settings.ELECTRUM} add_request {btc_amount} -w {wallet.path()}").read()
        # request = json.loads(request)

        # btc_address = request['address']
        btc_address = 'bc1q40jsjcn6290mtc988uut24nx7t8n49639lyukx'
        crypto_address = CryptoAddress.objects.create(
            address=btc_address,
            wallet_id=wallet,
            cad_due=cad_amount,
            btc_due=btc_amount
        )

        return crypto_address
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
    is_used         = models.BooleanField(default=False)
    is_paid         = models.BooleanField(default=False)
    date_created    = models.DateTimeField(auto_now_add=True)

    objects = CryptoAddressManager()


    def __str__(self):
        if self.is_used == True:
            return f"{self.address[:8]}....{self.address[-4:]} (used)"
        else:
            return f"{self.address[:8]}....{self.address[-4:]}"


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


    def confirm_full_payment(self, balance):
        '''
        Checks if the balance in the address is the same (or almost the same) as the balance owed.
        **Does not check if BTC prices are the same as when the payment request was first generated!
        Returns boolean 'is_paid'
        '''
        bal_conf    = balance['confirmed']
        abs_tol = 0.000009

        is_paid = isclose(bal_conf, self.btc_due, abs_tol=abs_tol)
        return is_paid



    def exchange_sanity_check(self, balance):
        '''
        Checks the current exchange rate to make sure 
        there hasn't been a huge drop between the time 
        the payment request was initiated to the time we 
        actually received the crypto.
        '''
        btc_price   = CryptoPrice.objects.filter(coin_fk__coin_name='bitcoin').last()
        bal_conf    = balance['confirmed']
        bal_cad     = bal_conf * btc_price.price
        is_close    =  isclose(bal_cad, self.cad_due, abs_tol=2)
        print('CAD due: ', self.cad_due)
        print('CAD balance: ', bal_cad)
            
        return is_close



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


    def qr(self):
        '''Creates an SVG QR-code for the BTC address'''
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=30,
            border=4
        )
        qr.add_data(self.address)
        factory = qrcode.image.svg.SvgPathImage
        img = qr.make_image(image_factory=factory)
        return img

    def save_qr(self, qr_img):
        '''
        Saves the QR code. I have decoupled this from self.qr() 
        because I will probably just save on the client-side. 
        But with multiple clients I will probably have to save 
        server-side.
        '''
        qr_img.save(f"{self.address[:8]}....{self.address[-4:]}3.svg")
        return










