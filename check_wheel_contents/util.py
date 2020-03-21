import base64
import hashlib
import re
from   typing  import List, Tuple

COMMA_SEP_RGX = re.compile(r'\s*,\s*')

class UserInputError(ValueError):
    """
    Subclass of `ValueError` raised whenever the user supplies an invalid value
    for something
    """
    pass


def comma_split(s: str) -> List[str]:
    return COMMA_SEP_RGX.split(s)

def bytes_signature(b: bytes) -> Tuple[int, str]:
    return (
        len(b),
        'sha256=' + urlsafe_b64encode_nopad(hashlib.sha256(b).digest()),
    )

def urlsafe_b64encode_nopad(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('us-ascii')
