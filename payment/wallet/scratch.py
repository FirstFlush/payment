import os
import binascii


print(binascii.hexlify(os.urandom(10)).decode())
# def _hmac(data=dict):
#     # key = settings.HMAC_KEY
#     key = 'bleh'
#     key = bytes(key, 'utf-8')
#     message = bytes(data, 'utf-8')
#     dig = hmac.new(key, message, hashlib.sha256)
#     return dig.hexdigest()


# print(_hmac('secret-key', 'wow important message'))

# print({'address'})