from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account



class AccountAdmin(UserAdmin):
    list_display = ('email', 'username', 'last_login', 'is_active','date_joined')
    list_display_link = ('email', 'username')
    readonly_fields = ('is_admin','is_staff','is_superadmin','last_login', 'date_joined')
    ordering = ('-date_joined',)
    search_fields = ['email']

    filter_horizontal = ()
    list_filter = ['is_staff']
    fieldsets = ()



admin.site.register(Account, AccountAdmin)