"""
Check wheel files for appropriate contents

Getting the right files into your wheel is tricky, and sometimes we mess up and
publish a wheel containing ``__pycache__`` directories or ``tests/``.  Do we
have to manually check the contents of every wheel we build before uploading it
to PyPI?  How about letting this program check for you?  Just run
``check-wheel-contents`` on your wheel, and it'll fail and notify you if any of
several common errors & mistakes are detected.  The errors are described in the
README, along with common causes and corresponding fixes.

Visit <https://github.com/jwodder/check-wheel-contents> for more information.
"""

__version__      = '0.2.0'
__author__       = 'John Thorvald Wodder II'
__author_email__ = 'check-wheel-contents@varonathe.org'
__license__      = 'MIT'
__url__          = 'https://github.com/jwodder/check-wheel-contents'
