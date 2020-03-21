import base64
import hashlib
import re

COMMA_SEP_RGX = re.compile(r'\s*,\s*')

class UserInputError(ValueError):
    """
    Subclass of `ValueError` raised whenever the user supplies an invalid value
    for something
    """
    pass


def comma_split(s):
    return COMMA_SEP_RGX.split(s)

def bytes_signature(b):
    return (
        len(b),
        'sha256=' + urlsafe_b64encode_nopad(hashlib.sha256(b).digest()),
    )

def urlsafe_b64encode_nopad(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('us-ascii')
