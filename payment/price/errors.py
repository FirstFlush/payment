


class CoinGeckoError(Exception):
    """Raised when Coin Gecko API call fails."""
    cli = '[API CALL FAILURE]  https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest '
    pass

class CoinMarketCapError(Exception):
    """Raised when CoinMarketCap API call fails."""
    cli = '[API CALL FAILURE]  https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest '
    

    pass

