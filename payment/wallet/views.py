from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import AddressNotification, CryptoAddress, CryptoWallet, PaymentRequest, Payment
from .serializers import PayRequestSerializer, PaymentSerializer
from payment.price.models import CryptoCoin, CryptoPrice

import decimal
import json

from django.urls import reverse
from django.conf import settings
from jsonrpclib import Server


class TestView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):

        payment = Payment.objects.last()
        serializer = PaymentSerializer(payment)
        payment.send_payment_details(serializer.data)
        
        return Response(serializer.data)


class PayRequestView(APIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        
        data = request.data
        wallet = get_object_or_404(CryptoWallet, slug='greatkart-wallet')
        wallet.load_wallet()
        cad_price = data['cad']
        #TODO: add datetime in request.data! so we can compare it to datetime of first address notification

        # get price:
        # TODO: check to make sure price is < 15 minutes ago.
        # TODO: if price is not less than 15 mins, raise error and do another API call 
        price = CryptoPrice.objects.filter(coin_fk__coin_name='bitcoin').last()
        btc_price = price.cad_to_btc(decimal.Decimal(cad_price))
        
        server = Server(settings.JSON_RPC)
        electrum_request = server.add_request(amount=float(btc_price), expiration=settings.PAY_REQUEST_EXPIRY, wallet=wallet.path(), force=True)

        address = CryptoAddress.objects.get_or_create(
            wallet_id=wallet,
            address=electrum_request['address']
        )[0]
        pr = PaymentRequest.objects.create(
            address_id = address,
            price_id = price,
            btc_due = btc_price,
            cad_due = cad_price,
        )

        print()
        print('notifying: ', reverse('notify'))
        address.notify('http://localhost:8000/wallet_api/notify/')
        print()

        serializer = PayRequestSerializer(pr)
        return Response(serializer.data)



class NotifyView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):

        data = request.data
        print('NotifyView data: ', data)

        address = get_object_or_404(CryptoAddress, address=data['address'])

        wallet = get_object_or_404(CryptoWallet, id=address.wallet_id.id)
        wallet.load_wallet()
        balance = address.get_balance()

        notification = AddressNotification.objects.create(
            address_id = address,
            btc_unconfirmed = decimal.Decimal(balance['unconfirmed']),
            btc_confirmed = decimal.Decimal(balance['confirmed'])
        )
        if notification.btc_confirmed > 0:
            payment = Payment.objects.payment_received(address=address, btc=notification.btc_confirmed)
            if payment.check_cad_acceptable() == True:
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









