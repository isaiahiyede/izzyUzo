#try:
from Crypto.Cipher import AES
from Crypto import Random

import base64

from django.conf import settings

#text_to_encrypt = '1234567890'

#secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', '1234567890123456')

secret_key_prefix = getattr(settings, 'AWS_ACCESS_KEY_ID', '12345678901234562367')
secret_key = "%s8732" %secret_key_prefix
#iv = Random.new().read(AES.block_size)

#cipher = AES.new(secret_key, AES.MODE_CFB, iv)
cipher = AES.new(secret_key, AES.MODE_ECB)

# except Exception as e:
#     print e
#     pass




def value_encryption(text_to_encrypt):
    #print 'text_to_encrypt: %s' %text_to_encrypt
    encoded = base64.b64encode(cipher.encrypt(text_to_encrypt.rjust(32)))
    #print 'encoded %s' %encoded
    return encoded

def value_decryption(encoded):
    #encoded = value_encryption(text_to_encrypt)
    decoded = cipher.decrypt(base64.b64decode(encoded)).strip()
    return decoded

