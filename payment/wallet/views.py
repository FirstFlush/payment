from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from jsonrpclib import Server

from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

# from payment.hmac_auth.client import HMACSigner
# from payment.hmac_auth.authentication import HMACAuthentication

from .errors import SendPaymentDetailsError
from .models import Balance, CryptoAddress, CryptoWallet, PaymentRequest, Payment, WalletApiFailure
from .serializers import NewRequestSerializer, NotificationSerializer, PayRequestSerializer, PaymentSerializer, TestSerializer
from payment.account.models import Account
# from payment.hmac_auth.authentication import HMACAuthentication

from payment.price.models import CryptoCoin, CryptoPrice
from payment.price.errors import OldPriceError

# from rest_framework_hmac.authentication import HMACAuthentication
import decimal
from datetime import datetime 

# from rest_framework_hmac import 

# # better to use the django-rest-framework-hmac library
# def _hmac(key, message):
#     key = bytes(key, 'utf-8')
#     message = bytes(message, 'utf-8')
#     dig = hmac.new(key, message, hashlib.sha256)
#     return dig.hexdigest()


# def _add_signature(data):
#     """Adds the HMAC signature as an extra key on the dictionary to be sent out as JSON"""
#     account = Account.objects.get(username='leaf')
#     hmac_key = HMACSigner(account)
#     # print('DATA: ', data)
#     signature = hmac_key.calc_signature(data)
#     key = account.hmac_key.key
#     data['signature'] = signature
#     data['key'] = key
#     print('signature received: ', signature)
#     return data


class TestView(APIView):
    # authentication_classes = []
    # authentication_classes = [HMACAuthentication,]
    permission_classes = []

    def post(self, request, *args, **kwargs):
        # d = {
        #     'address':'bc1fdjskafjsadlfjdsaklfjzfsda',
        #     'btc_confirmed':'100',
        #     'cad_exchange':'1000',
        #     'status':'paid',
        #     # 'date_created': datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S"),
        # }
        # _add_signature(d)
        # user = User.objects.create(
        #     username = 'club',
        #     password = 'asdfasd',
        #     email = 'dffub@blub.com'
        # )
        # print(user)
        return Response()


        # payment = Payment.objects.last()
        # serializer = PaymentSerializer(payment)
        # try:
        #     payment.send_payment_details(serializer.data)
        # except SendPaymentDetailsError as e:
        #     error = e.__class__.__name__
        #     WalletApiFailure.objects.create(
        #         error=error,
        #         notes = f"payment ID: {payment.id}"
        #     )
        # return Response(serializer.data)



class SerializerTest(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        data = request.data
        # stream = io.BytesIO(request.data)
        # data = JSONParser().parse(stream)
        serializer = TestSerializer(data=data)
        if serializer.is_valid():
            resp =serializer.validated_data
        else:
            resp = serializer.errors
        print(resp)
        return Response(resp)



class PayRequestView(APIView):
    # authentication_classes = [TokenAuthentication,]
    # permission_classes = [IsAuthenticated]
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):

        # print(request.auth)
        data = request.data

        serializer = NewRequestSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            valid_data =serializer.validated_data

        wallet = get_object_or_404(CryptoWallet, slug='greatkart-wallet')
        wallet.load_wallet()
        cad_price = valid_data['cad']
        #TODO: add datetime in request.data! so we can compare it to datetime of first address notification

        price = CryptoPrice.objects.filter(coin_fk__coin_name='bitcoin').last()
        # try:
        #     price.check_time()
        # except OldPriceError:
               # TODO: some function that tries all the price-fetching APIs? hmm 
        #     return HttpResponseBadRequest()

        btc_price = price.cad_to_btc(decimal.Decimal(cad_price))
        
        server = Server(settings.JSON_RPC)
        electrum_request = server.add_request(amount=float(btc_price), expiration=settings.PAY_REQUEST_EXPIRY, wallet=wallet.path(), force=True)

        address = CryptoAddress.objects.get_or_create(
            wallet_id=wallet,
            address=electrum_request['address']
        )[0]

        pr = PaymentRequest.objects.create(
            address_id = address,
            btc_due = btc_price,
            cad_due = cad_price,
        )

        address.notify('http://localhost:8888/wallet_api/notify/')

        serializer = PayRequestSerializer(pr)
        # json = JSONRenderer().render(serializer.data)
        # return Response(json)
        return Response(serializer.data)


# NotifyView request.data:
# =====================
# data = {
#   'address': 'bc1q2y0er7czna4qyewyvnsjpthkv6309tpae4mruy', 
#   'status': 'c5306e296471bbeb2f7a17ee169634be1a88689238facb03c38cf70397ef0fdf'
# }
class NotifyView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):

        data = request.data
        # data = {'address':'bc1qvvedv5lql9094pua5fjl0c5fh53nf0tepnvahr','status':'1232132321'}
        # data = {'address':'bc1qufrj36uzyl3l5ap9jr08akrk2mtla7e045gayd','status':'6454546454'}
        serializer = NotificationSerializer(data=data)
        if serializer.is_valid(raise_exception=True):

            print('notify data incoming: ', data)
            address = get_object_or_404(CryptoAddress, address=serializer.validated_data['address'])

            wallet = get_object_or_404(CryptoWallet, id=address.wallet_id.id)
            wallet.load_wallet()
            address_balance = address.get_balance()

            balance = Balance(
                address_id = address,
                btc_unconfirmed = decimal.Decimal(address_balance['unconfirmed']),
                btc_confirmed = decimal.Decimal(address_balance['confirmed']),
                txid = serializer.validated_data['status']
            )
            if balance.is_txid_duplicate() == True:
                print('duplicate TXID')
                pass
            else:
                balance.save()
                if balance.is_confirmed_balance_change() == True:
                    payment = Payment.objects.payment_received(address=address, btc=balance.btc_confirmed)
                    print('Payment: ', payment.__dict__)
                    if payment.is_btc_acceptable() == True:
                        address.notify_stop()
                    serializer = PaymentSerializer(payment)
                    payment.send_payment_details(serializer.data)

        return Response()


















# @api_view(['POST'])
# @permission_classes((permissions.AllowAny,))
# def notification(request):

#     if request.method != 'POST':
#         return HttpResponseBadRequest
    
#     data = request.data
#     print(data)

#     address = get_object_or_404(CryptoAddress, address=data['address'])
#     wallet = get_object_or_404(CryptoWallet, id=address.wallet_id.id)
#     wallet.load_wallet()
#     balance = address.get_balance()

#     AddressNotification.objects.create(
#         address_id = address,
#         btc_unconfirmed = balance['unconfirmed'],
#         btc_confirmed = balance['confirmed']
#     )


    # print(address.confirm_full_payment(balance))
    # print(address.currency_sanity_check(balance))
    # electrum notify POST request:
    # body = {
    #     "address"   : "bc1qkfcwrwva3s82j3m4uyv7zvvsgqk9kc36ggykw2", 
    #     "status"    : "3742b7c6e559d347734a4c4cdd40fded22458fd6b43f9a2f78d61a990c5ca712"},

    # return HttpResponse('hihih')






# @api_view(['POST'])
# @permission_classes((permissions.AllowAny,))
# def vendor_request_test(request):

#     if request.method != 'POST':
#         return HttpResponseBadRequest

#     # get wallet:
#     # TODO: how to clean the data? do i treat this like a form?
#     data = request.data
#     wallet = get_object_or_404(CryptoWallet, vendor_key=data['api-key'])
#     wallet.load_wallet()
#     cad_price = data['cad']

#     # get price:
#     # TODO: check to make sure price is < 15 minutes ago.
#     # TODO: if price is not less than 15 mins, raise error and do another API call 
#     price = CryptoPrice.objects.filter(coin_fk__coin_name='bitcoin').last()
#     btc_price = price.cad_to_btc(decimal.Decimal(cad_price))
    
#     # create address and request:
#     payment_request = PaymentRequest.objects.add_request(
#         wallet=wallet,
#         cad_amount=cad_price,
#         btc_amount=btc_price
#     )
#     address = payment_request.address_id

#     # set up notification and close wallet.
#     address.notify('http://localhost:8000/wallet_api/notification/')
#     wallet.close_wallet()

#     data = payment_request.details()
#     serializer = PayRequestSerializer(data)

#     # address.delete()

#     return Response(serializer.data)









