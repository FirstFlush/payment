from hmac import HMAC
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from jsonrpclib import Server

# from rest_framework.decorators import api_view, permission_classes
# from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle

from payment.hmac_auth.client import HMACSigner, hmac_sign
from payment.hmac_auth.authentication import HMACAuthentication

from .errors import SendPaymentDetailsError
from .models import Balance, CryptoAddress, CryptoWallet, PaymentRequest, Payment, WalletApiFailure
from .permissions import IsWalletOwner
from .serializers import NewRequestSerializer, NotificationSerializer, PayRequestSerializer, PaymentSerializer, TestSerializer
from .throttle import NotifyThrottle, PlanThrottle

from payment.account.models import Account
from payment.price.models import CryptoCoin, CryptoPrice
from payment.price.errors import OldPriceError

import decimal
from datetime import datetime 
import requests





class PayRequestView(APIView):

    authentication_classes = [HMACAuthentication]
    permission_classes = [IsWalletOwner]
    # throttle_classes = []
    # model = 'CryptoWallet'

    def post(self, request, *args, **kwargs):

        # print(request.auth)
        data = request.data
        serializer = NewRequestSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            valid_data = serializer.validated_data
        wallet = get_object_or_404(CryptoWallet, slug='leaf-wallet', account_id=request.user)
        wallet.load_wallet()
        cad_price = valid_data['cad']
        #TODO: add datetime in request.data! so i can compare it to datetime of first address notification

        price = CryptoPrice.objects.filter(coin_fk__coin_name='bitcoin').last()
        # try:
        #     price.check_time()
        # except OldPriceError:
        #     print('old price error! fetch updated price!')
        #     #    TODO: some function that tries all the price-fetching APIs? hmm 
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

        # address.notify('http://localhost:8888/wallet_api/notify/')

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

    # throttle_classes = [AnonRateThrottle]
    throttle_classes = []
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        data = request.data
        # data = {'address':'bc1qr3gsu3kpkunxx6hu6czev6g57qmfrnk6zplzxp','status':'1232132321'}
        serializer = NotificationSerializer(data=data)
        # serializer.validate_status(data['status'])
        if serializer.is_valid():

            print('notify data incoming: ', data)
            address = get_object_or_404(CryptoAddress, address=serializer.validated_data['address'])

            wallet = get_object_or_404(CryptoWallet, id=address.wallet_id.id)
            wallet.load_wallet()
            address_balance = address.get_balance()

            print('About to create balance object')
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
                    account = wallet.account_id
                    headers = hmac_sign(account, serializer.data)
                    try:
                        payment.send_payment_data(serializer.data, headers)
                    except SendPaymentDetailsError as e:
                        print(e.status_code)
        else:
            print('ELSE: ', request.data)

        return Response()













# class TestReceiveView(APIView):
#     authentication_classes = [HMACAuthentication]
#     # authentication_classes = []
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         print('dis a get')
#         return Response()

#     def post(self, request, *args, **kwargs):
#         print('----****----****----****')
#         print('\twoooooow')
#         print('****----****----****----')

#         return Response()


# class TestView(APIView):
#     # authentication_classes = []
#     # authentication_classes = [HMACAuthentication,]
#     permission_classes = []

#     def post(self, request, *args, **kwargs):

#         account = Account.objects.last()
#         hmac_signer = HMACSigner(account)

#         data = {
#             'cad': str(22.84),
#             # 'address':'bc1fdjskafjsadlfjdsaklfjzfsda',
#             # 'btc_confirmed':'100',
#             # 'cad_exchange':'1000',
#             # 'status':'paid',
#             # 'date_created': datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S"),
#         }
#         signature = hmac_signer.calc_signature(data=data)
#         print(signature)
#         headers = {
#             'signature'  : signature,
#             'vendor' : 'd5c8eecff17c1addd86106a2cb5365081d14477e'
#         }

#         url = 'http://192.168.1.65:8888/wallet_api/test_receive/'
#         requests.post(url, data=data, headers=headers)


#         return Response()























