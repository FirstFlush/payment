from django.contrib import admin

from .models import Plan, ThrottleRate


class PlanAdmin(admin.ModelAdmin):

    list_display = [
        'plan_name',
        'price',
        'usage_rate',
        'date_created',
    ]


class ThrottleRateAdmin(admin.ModelAdmin):

    list_display = [
        'burst',
        'sustained',
    ]



admin.site.register(Plan, PlanAdmin)
admin.site.register(ThrottleRate, ThrottleRateAdmin)
