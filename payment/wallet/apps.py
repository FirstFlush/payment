from django.apps import AppConfig


class CryptoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payment.wallet'


    def ready(self):
        from . import signals