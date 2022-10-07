from django.db import models
from django.conf import settings
from django_cryptography.fields import encrypt
from django.utils.text import slugify
from error.errors import WalletCloseError, WalletLoadError

from price.models import CryptoCoin, CryptoPrice
from account.models import Account

import json
import decimal
import os
import qrcode
import qrcode.image.svg
from math import isclose
import hashlib


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


class CryptoWalletManager(models.Manager):

    def create_wallet(self, wallet_name, account, is_vendor):
        '''Create a brand new wallet'''

        new_wallet = CryptoWallet(
            accuont_id=account,
            wallet_name=wallet_name,
            is_vendor=is_vendor,
            slug=slugify(wallet_name)
        )

        create_wallet = json.loads(os.popen(f"{settings.ELECTRUM} create -w {new_wallet.slug}").read())
        seed = create_wallet['seed']
        os.popen(f"{settings.ELECTRUM} load_wallet -w {new_wallet.slug}")
        # new_wallet.mpk = json.loads(os.popen(f"{settings.ELECTRUM} getmpk -w {new_wallet.slug}").read())
        new_wallet.load_wallet()
        new_wallet.vendor_key = new_wallet.vendor_keygen(new_wallet.mpk)
        new_wallet.save()

        return new_wallet


    def restore_wallet(self, account, wallet_name, is_vendor, mpk):
        '''Restores a wallet from MPK'''

        new_wallet = CryptoWallet(
            account_id=account,
            wallet_name=wallet_name,
            is_vendor=is_vendor,
            slug=slugify(wallet_name),
            mpk=mpk
        )

        restored_wallet = os.popen(f"{settings.ELECTRUM} restore {new_wallet.mpk} -w {new_wallet.path()}").read()
        
        new_wallet.load_wallet()
        # os.popen(f"{settings.ELECTRUM} load_wallet -w {new_wallet.path()}")
        new_wallet.vendor_key = new_wallet.vendor_keygen(new_wallet.mpk)
        new_wallet.save()


class CryptoWallet(models.Model):

    account_id  = models.ForeignKey(to=Account, on_delete=models.CASCADE)
    wallet_name = models.CharField(max_length=255, unique=True)
    vendor_key  = models.CharField(max_length=255, unique=True)
    mpk         = models.CharField(max_length=255, unique=True)
    slug        = models.SlugField(max_length=255, unique=True)
    is_vendor   = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)

    objects = CryptoWalletManager()


    def path(self):
        if self.slug == 'default-wallet':
            file_name = 'default_wallet'
        else:
            file_name = self.slug
        return f"{settings.WALLET_DIR}/{file_name}"


    def mpk_short(self):
        '''Returns easier to read version of MPK'''
        return f"{self.mpk[:8]}....{self.mpk[-4:]}"


    def vendor_keygen(self):
        '''Generates a vendor key using the SHA3-224 hashing algorithm'''
        return hashlib.sha3_224(self.mpk.encode('utf-8')).hexdigest()


    def load_wallet(self):
        '''Loads the wallet in the Electrum daemon'''
        loaded = json.loads(os.popen(f"{settings.ELECTRUM} load_wallet -w {self.path()}").read())
        if loaded == True:
            return loaded
        else:
            raise WalletLoadError
    

    def close_wallet(self):
        '''Closes the wallet in the Electrum daemon'''
        closed = json.loads(os.popen(f"{settings.ELECTRUM} close_wallet -w {self.path()}").read())
        if closed == True:
            return closed
        else:
            raise WalletCloseError

    def __str__(self):
        return self.wallet_name




class CryptoAddressManager(models.Manager):

    def add_request(self, wallet, cad_amount, btc_amount):
        # # the actual code:
        # request = os.popen(f"{settings.ELECTRUM} add_request {btc_amount} -w {wallet.path()}").read()
        # request = json.loads(request)
        # btc_address = request['address']
        
        btc_address = 'bc1q8zxq2dlfl38p5r95wl50z3tgty97hpugxjmsr7'
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


    def payment_details(self):
        '''Prepare a dict to serialize into JSON and send back to the vendor.'''
        pay_details = {
            'address'   : self.address,
            'btc_due'   : self.btc_due,
            'qr_code'   : self.qr(),
        }
        return pay_details


    def currency_sanity_check(self, balance):
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


    def list_addresses(self, wallet):
        '''Returns a list of all addresses in the wallet'''
        addys = os.popen(f"{settings.ELECTRUM} listaddresses -w {wallet.path()}").read()
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










