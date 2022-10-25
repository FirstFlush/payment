
class OrphanPaymentError(Exception):
    """Raised when PaymentRequest can not be found that matches the Payment received."""
    pass


class SendPaymentDetailsError(Exception):
    """Raised when sending payment details to vendor URL returns 404 error"""
    pass

class CurrencySanityError(Exception):
    '''Raised when the $CAD received is different from $CAD expected'''
    pass


class SeriousOverPayment(Exception):
    '''Raised when crypto payment far exceeds Address' btc_due'''
    pass


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
