import base64
import hashlib
from   os.path import splitext
import re

COMMA_SEP_RGX = re.compile(r'\s*,\s*')

def comma_split(s):
    return COMMA_SEP_RGX.split(s)

def bytes_signature(b):
    return (
        len(b),
        'sha256=' + urlsafe_b64encode_nopad(hashlib.sha256(b).digest()),
    )

def urlsafe_b64encode_nopad(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('us-ascii')

def get_ext(path):
    return splitext(path.split('/')[-1])[1]
