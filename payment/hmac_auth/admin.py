from django.contrib import admin
from .models import HMACKey


class HMACKeyAdmin(admin.ModelAdmin):

    list_display = [
        'key',
        'account_id',
    ]



admin.site.register(HMACKey, HMACKeyAdmin)