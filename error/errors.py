

class ExchangeSanityError(Exception):
    '''Raised when the $CAD received is different from $CAD expected'''
    pass

class PriceApiFailure(Exception):
    '''raised when a crypto price-fetching API fails'''
    pass

# class UnderPayment(Exception):
#     '''
#     Raised when crypto payment amount does not meet Address'
#     btc_due attribute, but is greater than 0
#     '''
#     pass

# class OverPayment(Exception):
#     '''Raised when crypto payment exceeds Address' btc_due'''
#     pass

# class Unpaid(Exception):
#     '''
#     Raised if we get BTC address notification but no 
#     crypto has been paid. Most likely transaction is 
#     still unconfirmed.
#     '''
#     pass