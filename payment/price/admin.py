from django.contrib import admin
from.models import CryptoCoin, CryptoPrice, PriceApiFailure


class CryptoCoinAdmin(admin.ModelAdmin):

    list_display = [
        'coin_name',
        'coin_name_short',
    ]


class CryptoPriceAdmin(admin.ModelAdmin):

    list_display =[
        'coin_fk',
        'price',
        'date_created',
    ]
    ordering = ['-date_created',]




class PriceApiFailureAdmin(admin.ModelAdmin):

    list_display = [
        'failed_api',
        'error',
        'date_created'
    ]




admin.site.register(CryptoCoin, CryptoCoinAdmin)
admin.site.register(CryptoPrice, CryptoPriceAdmin)
admin.site.register(PriceApiFailure, PriceApiFailureAdmin)
