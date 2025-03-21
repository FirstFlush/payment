from distutils.util import byte_compile
from django.db import models
from django.conf import settings
from django_cryptography.fields import encrypt
from django.utils.text import slugify
from .errors import WalletCloseError, WalletLoadError, SendPaymentDetailsError, OrphanPaymentError

from payment.account.models import Account
from payment.plan.models import Plan
from payment.price.models import CryptoCoin, CryptoPrice

import json
import decimal
import os
import qrcode
import qrcode.image.svg
from math import isclose
from jsonrpclib import Server
import hashlib
import requests
import subprocess
# import asyncio
# import time


def _start_daemon():
    """Starts the electrum daemon."""
    subprocess.run([f"{settings.ELECTRUM}", 'daemon', '-d'])



class CryptoWalletManager(models.Manager):

    def create_wallet(self, wallet_name, account, is_vendor):
        """Create a brand new wallet"""

        new_wallet = CryptoWallet(
            accuont_id=account,
            wallet_name=wallet_name,
            is_vendor=is_vendor,
            slug=slugify(wallet_name)
        )

        create_wallet = json.loads(os.popen(f"{settings.ELECTRUM} create -w {new_wallet.slug}").read())
        seed = create_wallet['seed']
        os.popen(f"{settings.ELECTRUM} load_wallet -w {new_wallet.slug}")
        new_wallet.load_wallet()
        # new_wallet.vendor_key = new_wallet.vendor_keygen(new_wallet.mpk)
        new_wallet.save()

        return new_wallet


    def restore_wallet(self, account, wallet_name, is_vendor, mpk):
        """Restores a wallet from MPK"""
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
        # new_wallet.vendor_key = new_wallet.vendor_keygen()
        new_wallet.save()
        return new_wallet


class CryptoWallet(models.Model):

    coin_id         = models.ForeignKey(to=CryptoCoin, on_delete=models.CASCADE)
    account_id      = models.ForeignKey(to=Account, on_delete=models.CASCADE)
    plan_id         = models.ForeignKey(to=Plan, on_delete=models.SET_NULL, null=True)
    wallet_name     = models.CharField(max_length=255, unique=True)
    wallet_code     = models.CharField(max_length=20)
    mpk             = models.CharField(max_length=255, unique=True)
    slug            = models.SlugField(max_length=255, unique=True)
    is_vendor       = models.BooleanField(default=False)
    is_active       = models.BooleanField(default=True)
    notify_url      = models.URLField(max_length=255, null=True, blank=True)

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


    # def vendor_keygen(self):
    #     '''Generates a vendor key using the SHA3-224 hashing algorithm'''
    #     return hashlib.sha3_224(self.mpk.encode('utf-8')).hexdigest()


    def load_wallet(self):
        """Loads the wallet in the Electrum daemon"""
        server = Server(settings.JSON_RPC)
        try:
            server.load_wallet(wallet_path=self.path(), password=settings.WALLET_PASS)
        except ConnectionRefusedError:
            _start_daemon()
            server.load_wallet(wallet_path=self.path(), password=settings.WALLET_PASS)
        return


    def close_wallet(self):
        '''Closes the wallet in the Electrum daemon'''
        server = Server(settings.JSON_RPC)
        server.close_wallet(wallet_path=self.path())
        return


    def __str__(self):
        return self.wallet_name


    def is_mine(self, address):
        #TODO: testing!
        """Confirms address does indeed belong to me"""
        server = Server(settings.JSON_RPC)
        return server.ismine(address=address, wallet=self.path())


    def listaddresses(self):
        '''Returns a list of all addresses in the wallet'''
        self.load_wallet()
        server = Server(settings.JSON_RPC)
        addys = server.listaddresses(wallet=self.path())
        self.close_wallet()
        return addys




class CryptoAddress(models.Model):

    wallet_id       = models.ForeignKey(to=CryptoWallet, on_delete=models.CASCADE, null=True, blank=True)
    address         = models.CharField(max_length=255, unique=True)
    # is_used         = models.BooleanField(default=False)
    date_created    = models.DateTimeField(auto_now_add=True)

    # objects = CryptoAddressManager()

    def __str__(self):
        return self.address
        # return f"{self.address[:8]}....{self.address[-4:]}"


    def get_balance(self):
        """
        Checks the address' balance. Returns a dict of decimals:
        {
            'confirmed' : 0.0034423,
            'unconfirmed' : 0,
        }
        """
        server = Server(settings.JSON_RPC)
        balance = server.getaddressbalance(self.address)

        return balance


    def notify(self, url=str):
        """Electrum notify command. Returns boolean"""
        server = Server(settings.JSON_RPC)
        notification =server.notify(self.address, url)
        return


    def notify_stop(self):
        """
        Returns nothing.
        Stops the notification monitoring of an address.
        """        
        server = Server(settings.JSON_RPC)
        server.notify(self.address, '') # '' is empty URL string to stop notifications
        return


    def currency_sanity_check(self, balance):
        """
        Checks the current exchange rate to make sure 
        there hasn't been a huge drop between the time 
        the payment request was initiated to the time we 
        actually received the crypto.
        """
        btc_price   = CryptoPrice.objects.filter(coin_fk__coin_name='bitcoin').last()
        bal_conf    = balance['confirmed']
        bal_cad     = bal_conf * btc_price.price
        is_close    =  isclose(bal_cad, self.cad_due, abs_tol=2)
        print('CAD due: ', self.cad_due)
        print('CAD balance: ', bal_cad)
            
        return is_close


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
        Saves the QR code. Returns nothing. I have decoupled this from self.qr() because I will probably 
        just save on the client-side. But with multiple clients I will probably have to save server-side.
        '''
        qr_img.save(f"{self.address[:8]}....{self.address[-4:]}3.svg")
        return


class RequestManager(models.Manager):


    """
    add_request electrum response:
    {
        "URI": "bitcoin:bc1q0jvf6pdsls8gcjm02yed3n6k6vzfywuvsfs75u?amount=0.00027921&time=1664956697&exp=3600",
        "address": "bc1q0jvf6pdsls8gcjm02yed3n6k6vzfywuvsfs75u",
        "amount_BTC": "0.00027921",
        "amount_sat": 27921,
        "expiration": 3600,
        "is_lightning": false,
        "message": "",
        "status": 0,
        "status_str": "Expires in about 1 hour",
        "timestamp": 1664956697
    }
    """


    def create_request(self, wallet, cad_amount, btc_amount):
        server = Server(settings.JSON_RPC)
        request = server.add_request(amount=float(btc_amount), wallet=wallet.path(), force=True)
        return request


        # address_hex = request['address']
        # print('address_hex :', address_hex)

        # # get_or_create() returns a tuple of (ModelInstance, Boolean) 
        # crypto_address = CryptoAddress.objects.get_or_create(
        #     address=address_hex,
        #     wallet_id=wallet,
        # ) 

        # payment_request = PaymentRequest.objects.create(
        #     address_id=crypto_address[0],
        #     btc_due=btc_amount,
        #     cad_due=cad_amount,
        # )

        # return payment_request


class PaymentRequest(models.Model):

    address_id      = models.ForeignKey(to=CryptoAddress, on_delete=models.CASCADE)
    btc_due         = models.DecimalField(decimal_places=7, max_digits=10)
    cad_due         = models.DecimalField(decimal_places=2, max_digits=10)
    is_paid         = models.BooleanField(default=False)
    date_created    = models.DateTimeField(auto_now_add=True)

    objects = RequestManager()

    # def __str__(self):
    #     address = self.address_id.address
    #     return f"{address[:8]}...{address[-4:]}: $ {self.cad_due}"


    def cad_min_allowance(self):
        """
        Returns decimal.
        """
        min_allowed_payment = self.cad_due * decimal.Decimal(settings.CAD_MIN_ALLOWANCE)
        return min_allowed_payment


    def details(self):
        """
        Method returns a dictionary of payment request details.
        *This is what gets sent back to the vendor when a customer is checking out.
        """
        pay_details = {
            'address'       : self.address_id.address,
            'btc_due'       : self.btc_due,
            # 'qr_code'       : self.qr(),
            'date_created'  : self.date_created
        }
        return pay_details


class Balance(models.Model):

    address_id      = models.ForeignKey(to=CryptoAddress, on_delete=models.CASCADE)
    btc_unconfirmed = models.DecimalField(decimal_places=7, max_digits=10, default=0)
    btc_confirmed   = models.DecimalField(decimal_places=7, max_digits=10, default=0)
    txid            = models.CharField(max_length=255)
    date_created    = models.DateTimeField(auto_now_add=True)


    def is_confirmed_balance_change(self) -> bool:
        """Checks if there are any other btc_confirmed balances 
        for this address. And if so, has the value changed from 
        the previous one."""
        prev_confirmed_balance = Balance.objects.filter(address_id=self.address_id, id__lt=self.id, btc_confirmed__gt=0).exclude(id=self.id).last()
        print('prev bal: ', prev_confirmed_balance)

        if hasattr(prev_confirmed_balance,'btc_confirmed'):
            if self.btc_confirmed != prev_confirmed_balance.btc_confirmed:
                return True
            else:
                print('has attr, no balance change')
                return False
        else: # prev_balance returns NoneType. No payments exist on address
            if self.btc_confirmed > 0:
                return True
            return False


    def check_full_payment(self) -> bool:
        """Checks if the btc_confirmed is >= to btc_due.
        *Confirms we received correct amount of BTC. Does NOT confirm 
        if currency conversion is wthin an acceptable range!
        """
        pay_request = PaymentRequest.objects.filter(address_id=self.address_id).last()
        if pay_request.btc_due >= self.btc_confirmed:
            pay_request.is_paid = True
            pay_request.save()
            return True
        return False


    def is_txid_duplicate(self):
        """Returns True if a recorded Balance has the same status value (TXID). 
        This method exists because for some reason Electrum sends 
        balance-change notification twice. Dunny why.
        """
        prev_balance = Balance.objects.filter(address_id=self.address_id, txid=self.txid).exclude(id=self.id).last()
        if hasattr(prev_balance, 'status'):
            return True
        return False



class PaymentManager(models.Manager):

    def payment_received(self, address, btc):
        """Creates a new Payment instance"""
        price = CryptoPrice.objects.filter(coin_fk__coin_name='bitcoin').last()
        cad = price.btc_to_cad(btc)
        new_payment = Payment(
            address_id = address,
            btc_confirmed = btc,
            cad_exchange = cad
        )
        try:
            pay_request = Payment.objects._find_pay_request(address)
        except OrphanPaymentError:
            new_payment.status = 'orphan_payment'
        else:
            new_payment.pay_request_id = pay_request
            new_payment._create_status()
        new_payment.save()
        return new_payment


    def _find_pay_request(self, address):
        """Finds PayRequest so we can link Payment to it. 
        returns OrphanPaymentError if no PayRequest object 
        is found."""
        pay_request = PaymentRequest.objects.filter(address_id=address).last()
        if pay_request != None:
            return pay_request
        else:
            raise OrphanPaymentError


class Payment(models.Model):

    STATUS_CHOICES = (
        ('paid','Paid'),
        ('underpaid', 'Underpaid'),
        ('overpaid', 'Overpaid'),
        ('orphan','Orphan')
    )

    address_id      = models.ForeignKey(to=CryptoAddress, on_delete=models.CASCADE)
    pay_request_id  = models.ForeignKey(to=PaymentRequest, on_delete=models.CASCADE, blank=True, null=True)
    btc_confirmed   = models.DecimalField(decimal_places=7, max_digits=10, default=0)
    cad_exchange    = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    status          = models.CharField(max_length=255, choices=STATUS_CHOICES)
    date_created    = models.DateTimeField(auto_now_add=True)

    objects = PaymentManager()


    def _create_status(self):
        """Sets the status attribute.
        Confirms if the BTC we received is (roughly) the same as the BTC due.
        """
        if self.pay_request_id == None:
            self.status = 'orphan'
            return
        crypto_due = self.pay_request_id.btc_due * settings.BTC_MIN_ALLOWANCE
        overpay = crypto_due * settings.OVERPAYMENT_THRESH

        if crypto_due <= self.btc_confirmed < overpay:
            self.status = 'paid'
        elif self.btc_confirmed < crypto_due:
            self.status = 'underpaid'
        elif self.btc_confirmed >= crypto_due * overpay:
            self.status = 'overpaid'
        return


    def send_payment_data(self, data, headers) -> bool:
        """Returns True if details successfully sent.
        Sends serialized data to vendor, confirming them of successful payment.
        """
        url = self.address_id.wallet_id.notify_url
        # url = 'http://localhost:8000/crypto/api/notify/' #TESTING PURPOSES ONLY!
        r = requests.post(url=url, data=data, headers=headers)
        if r.status_code != 200:
            raise SendPaymentDetailsError

        return True


    def is_cad_acceptable(self) -> bool:
        """Returns bool.
        Compares the CAD amount received with the CAD amount requested.
        If CAD received is too low self.is_problem becomes True.
        """
        if self.cad_exchange >= self.pay_request_id.cad_due:
            return True
        if self.cad_exchange >= self.pay_request_id.cad_min_allowance():
            return True
        else:
            #TODO what to do instead of self.is_problem?
            # self.is_problem = True
            self.save()

        return False


    def is_btc_acceptable(self) -> bool:
        """Checks if BTC payment is within 
        acceptable minimum allowance, as defined by the vendor. 
        **This min-allowance number should be close to 100%. 0.98 for now.
        """
        try:
            min_allow = self.pay_request_id.btc_due * settings.BTC_MIN_ALLOWANCE
            if self.btc_confirmed >= min_allow:
                return True
            else:
                return False
        except AttributeError:
            return True





# class VendorPayment(models.Model):

#     wallet_id       = models.ForeignKey(to=CryptoWallet, on_delete=models.CASCADE)
#     address         = models.CharField(max_length=255)
#     amount_btc      = models.DecimalField(max_digits=20, decimal_places=7)
#     date_created    = models.DateTimeField(auto_now_add=True)









class WalletApiFailure(models.Model):
    # TODO: is this necessary? explore basic logging practices before building this.
    
    error           = models.CharField(max_length=255)
    date_created    = models.DateTimeField(auto_now_add=True)
    details         = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Wallet API Failure'
        verbose_name_plural = 'Wallet API Failures'










