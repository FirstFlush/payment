# import os

# from electrum.electrum.commands import Commands
# from electrum.electrum.simple_config import SimpleConfig
# from electrum.electrum.network import Network
# from electrum.electrum.daemon import Daemon

# cmd = Commands()
import decimal
from django.urls import reverse

import hmac
import hashlib

from rest_framework_hmac.hmac_key.models import HMACKey


def _hmac(data=dict):
    # key = settings.HMAC_KEY
    key = 'bleh'
    key = bytes(key, 'utf-8')
    message = bytes(data, 'utf-8')
    dig = hmac.new(key, message, hashlib.sha256)
    return dig.hexdigest()


print(_hmac('secret-key', 'wow important message'))
