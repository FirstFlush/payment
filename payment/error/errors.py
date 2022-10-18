

class SendPaymentDetailsError(Exception):
    """Raised when sending payment details to vendor URL returns 404 error"""
    pass

class CurrencySanityError(Exception):
    '''Raised when the $CAD received is different from $CAD expected'''
    pass

class PriceFetchApiFailure(Exception):
    '''Raised when a crypto price-fetching API fails'''
    pass

class PriceOutdatedError(Exception):
    '''
    Raised when the most recent crypto 
    price in the database is more than 
    15 minutes out of date
    '''
    pass

class SeriousOverPayment(Exception):
    '''Raised when crypto payment far exceeds Address' btc_due'''
    pass


# class CryptoAddressUniqueConstraintFailed(Exception):
#     '''Raised when a new CryptoAddress fails to create because the address is already in the DB'''    
#     pass

class WalletLoadError(Exception):
    '''Raised when a wallet fails to laod with the 'electrum load_wallet' command'''
    pass

class WalletCloseError(Exception):
    '''Raised when a wallet fails to close with the 'electrum close_wallet' command'''
    pass

class WalletCreateError(Exception):
    '''Raised when 'electrum create' command fails.'''
    pass

class WalletRestoreError(Exception):
    '''Raised when 'electrum restore' command fails.'''
    pass

class ElectrumException(Exception):
    '''General electrum error'''
    pass





# class UnderPayment(Exception):
#     '''
#     Raised when crypto payment amount does not meet Address'
#     btc_due attribute, but is greater than 0
#     '''
#     pass

# class Unpaid(Exception):
#     '''
#     Raised if we get BTC address notification but no 
#     crypto has been paid. Most likely transaction is 
#     still unconfirmed.
#     '''
#     pass