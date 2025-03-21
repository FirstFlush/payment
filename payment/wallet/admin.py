from django.contrib import admin
from .models import CryptoAddress, CryptoWallet, PaymentRequest, Balance, Payment#, VendorPayment




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
        'date_created',
    ]
    list_filter = [
        'wallet_id',
    ]
    search_fields = [
        'address',
    ]


class BalanceAdmin(admin.ModelAdmin):
    list_display = [
        'address_id',
        'btc_unconfirmed',
        'btc_confirmed',
        'date_created',
    ]
    list_filter = [
        'btc_unconfirmed',
        'btc_confirmed',
    ]


class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = [
        'address_id',
        'btc_due',
        'cad_due',
        'is_paid',
        'date_created',
    ]

class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'address_id',
        'status',
        'btc_confirmed',
        'cad_exchange',
        'date_created',
    ]


# class VendorPaymentAdmin(admin.ModelAdmin):

#     list_display = [
#         'wallet_id',
#         'amount_btc',
#         'date_created',
#     ]

admin.site.register(CryptoWallet, CryptoWalletAdmin)
admin.site.register(CryptoAddress, CryptoAddressAdmin)
admin.site.register(PaymentRequest, PaymentRequestAdmin)
admin.site.register(Balance, BalanceAdmin)
admin.site.register(Payment, PaymentAdmin)
# admin.site.register(VendorPayment, VendorPaymentAdmin)