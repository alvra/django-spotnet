try:
    from Crypto.PublicKey import RSA
except ImportError:
    print 'Could not import Crypto.PublicKey.RSA, so post signature " \
        "will not be validated.'  # TODO: log this instead
    RSA = None


# DOCUMENTATION OF PyCrypto
# https://www.dlitz.net/software/pycrypto/api/current/toc-Crypto.PublicKey.RSA-module.html
# https://github.com/dlitz/pycrypto/blob/master/lib/Crypto/PublicKey/RSA.py


def verify(modulus, exponent, message, signature):
    if RSA:
        rsa = RSA((modulus, exponent))
        return rsa._verify(message, signature)
    else:
        return True


def sign(modulus, exponent, private_exp, message):
    if RSA:
        rsa = RSA((modulus, exponent, private_exp))
        result = rsa._sign(message)
        return result[0]
    else:
        return ''
