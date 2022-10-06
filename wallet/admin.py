from django.contrib import admin
from .models import CryptoAddress, CryptoWallet




class CryptoWalletAdmin(admin.ModelAdmin):
    
    list_display = [
        'account_id',
        'wallet_name',
        # 'slug',
        'mpk_short',
        'is_vendor',
    ]

    # prepopulated_fields = {'slug':('wallet_name',)}


class CryptoAddressAdmin(admin.ModelAdmin):
    
    list_display = [
        'wallet_id',
        'address',
        'btc_due',
        'cad_due',
        'btc_paid',
        'is_paid',
        'date_created',
    ]
    list_filter = [
        'wallet_id',
    ]
    search_fields = [
        'address',
    ]







admin.site.register(CryptoWallet, CryptoWalletAdmin)
admin.site.register(CryptoAddress, CryptoAddressAdmin)
