# import os

# from electrum.electrum.commands import Commands
# from electrum.electrum.simple_config import SimpleConfig
# from electrum.electrum.network import Network
# from electrum.electrum.daemon import Daemon

# cmd = Commands()
import decimal


cad_due = 122.51

PERCENT_ALLOW = 0.95

cad_received = 121.41

allow_threshold = 40 * PERCENT_ALLOW

print(allow_threshold)

min_allowed_payment = 0.52 * decimal.Decimal(12)
