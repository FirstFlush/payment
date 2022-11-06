
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import exceptions
from rest_framework.permissions import BasePermission, IsAuthenticated

from .models import CryptoWallet
from payment.account.models import Account
from payment.plan.models import Plan



class IsPlanAllow(BasePermission):
    
    def has_permission(self, request, view):
        wallet_code = request.META.get('HTTP_WALLET')
        try:
            CryptoWallet.objects.get(account_id=request.user, wallet_code=wallet_code)
        except CryptoWallet.DoesNotExist:
            return False
        else:
            pass

class IsWalletOwner(BasePermission):

    def has_permission(self, request, view):

        wallet_code = request.META.get('HTTP_WALLET')
        try:
            CryptoWallet.objects.get(account_id=request.user, wallet_code=wallet_code)
        except CryptoWallet.DoesNotExist:
            return False
        else: 
            return True
