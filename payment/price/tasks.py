
from .models import CryptoPrice, PriceApiFailure
from .errors import CoinGeckoError, CoinMarketCapError

from celery import shared_task


@shared_task
def fetch_price():
    """Fetches crypto price from coingecko.com & coinmarketcap.com.
    Creates a PriceApiFailure database entry if either API call fails.
    """
    try:
        CryptoPrice.objects.coingecko()
    except CoinGeckoError as e:
        error = e.__class__.__name__
        PriceApiFailure.objects.create(error=error)

        try:
            CryptoPrice.objects.coinmarketcap()
        except CoinMarketCapError as e:
            error = e.__class__.__name__
            PriceApiFailure.objects.create(error=error)
    return


@shared_task
def delete_old_prices():
    """Ran daily by celery to delete old prices
    """
    print('hihihi')
    CryptoPrice.objects.delete_old()
    return

