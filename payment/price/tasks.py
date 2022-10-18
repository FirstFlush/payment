from celery import shared_task
from .models import CryptoPrice

@shared_task
def add(x,y):
    print()
    print('hellooooo :) ')
    return x + y


@shared_task
def fetch_price():
    CryptoPrice.objects.coingecko()
    return