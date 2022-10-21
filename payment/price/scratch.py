# from .models import CryptoPrice
# from .errors import CoinGeckoError

class CoinGeckoError(Exception):
    pass



def thing():
    try:
        1 / 0
    except:
        raise CoinGeckoError


print('******************')
thing()
print('******************')