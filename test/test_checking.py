import pytest
from   check_wheel_contents.checker  import COMMON_NAMES, WheelChecker
from   check_wheel_contents.checks   import Check, FailedCheck
from   check_wheel_contents.contents import WheelContents
from   check_wheel_contents.filetree import Directory, File

@pytest.mark.parametrize('rows,failures', [
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=UxbST6sF1RzAkvG8kCt15x13QBsB5FPeLnRJ4wHMqps',
                '1003',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=UxbST6sF1RzAkvG8kCt15x13QBsB5FPeLnRJ4wHMqps',
                '1003',
            ],
            [
                'foo.pyc',
                'sha256=ZjTs9Wx4pXxwT5mNZJ8WoAt-9zeO9iaxYhNFES7BrIY',
                '1040',
            ],
        ],
        [FailedCheck(Check.W001, ['foo.pyc'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=UxbST6sF1RzAkvG8kCt15x13QBsB5FPeLnRJ4wHMqps',
                '1003',
            ],
            [
                'foo.pyo',
                'sha256=ZjTs9Wx4pXxwT5mNZJ8WoAt-9zeO9iaxYhNFES7BrIY',
                '1040',
            ],
        ],
        [FailedCheck(Check.W001, ['foo.pyo'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=UxbST6sF1RzAkvG8kCt15x13QBsB5FPeLnRJ4wHMqps',
                '1003',
            ],
            [
                '__pycache__/foo.cpython-36.pyc',
                'sha256=ZjTs9Wx4pXxwT5mNZJ8WoAt-9zeO9iaxYhNFES7BrIY',
                '1040',
            ],
        ],
        [FailedCheck(Check.W001, ['__pycache__/foo.cpython-36.pyc'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=UxbST6sF1RzAkvG8kCt15x13QBsB5FPeLnRJ4wHMqps',
                '1003',
            ],
            [
                '__pycache__/foo.cpython-36.opt-1.pyc',
                'sha256=ZjTs9Wx4pXxwT5mNZJ8WoAt-9zeO9iaxYhNFES7BrIY',
                '1040',
            ],
        ],
        [FailedCheck(Check.W001, ['__pycache__/foo.cpython-36.opt-1.pyc'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo/__init__.py',
                'sha256=f6qW0sceqJJFaqOMuDCf8aLvlAGGSAqMUv6_5fmEqnU',
                '986',
            ],
            [
                'foo/bar.py',
                'sha256=13nkC_buM-u8_X465GXhWtLBXiiwxDyKwzPXHcHfGZ8',
                '1002',
            ],
            [
                'foo/__pycache__/__init__.cpython-36.pyc',
                'sha256=rHJbQE_4bKobwU3-bMSwroezXhWdAD_WGeVskhfmJfs',
                '1031',
            ],
            [
                'foo/__pycache__/bar.cpython-36.pyc',
                'sha256=_Bwzc6pX7GqAcXhljEKl0rhdf_ddb-X5vRfU0MztA4s',
                '1075',
            ],
            [
                'foo/subfoo/__init__.py',
                'sha256=Nklhzg65B016HWZdCkOOV8Wj3HkSmIUPnyeTmXXSmyo',
                '1058',
            ],
            [
                'foo/subfoo/__pycache__/__init__.cpython-36.pyc',
                'sha256=ZcfO0RZv7YeeyIaZSMQAVHJjsjRsiwj85m3zqKZX4Kg',
                '1010',
            ],
        ],
        [FailedCheck(
            Check.W001,
            [
                'foo/__pycache__/__init__.cpython-36.pyc',
                'foo/__pycache__/bar.cpython-36.pyc',
                'foo/subfoo/__pycache__/__init__.cpython-36.pyc',
            ],
        )],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=UxbST6sF1RzAkvG8kCt15x13QBsB5FPeLnRJ4wHMqps',
                '1003',
            ],
            [
                'foo-1.0.dist-info/how-did-this-get-here.pyc',
                'sha256=iKmjZrSZ3et2vMFF_Wxmtv6mjmci6Gm8TyvAeu9KT7s',
                '988',
            ],
        ],
        [FailedCheck(Check.W001, ['foo-1.0.dist-info/how-did-this-get-here.pyc',])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/platlib/foo.py',
                'sha256=9LpEj5Zw0laBNRM8ENYpfQmkjxRIy8tKOObUEpNy6NA',
                '1040',
            ],
            [
                'foo-1.0.data/platlib/__pycache__/foo.cpython-36.pyc',
                'sha256=6_TatpFL-LF3q8NAOEPPGuZVXrq0epNoKRyk_HVRoiM',
                '980',
            ],
        ],
        [FailedCheck(Check.W001, ['foo-1.0.data/platlib/__pycache__/foo.cpython-36.pyc'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/other/foo.py',
                'sha256=9LpEj5Zw0laBNRM8ENYpfQmkjxRIy8tKOObUEpNy6NA',
                '1040',
            ],
            [
                'foo-1.0.data/other/__pycache__/foo.cpython-36.pyc',
                'sha256=6_TatpFL-LF3q8NAOEPPGuZVXrq0epNoKRyk_HVRoiM',
                '980',
            ],
        ],
        [FailedCheck(Check.W001, ['foo-1.0.data/other/__pycache__/foo.cpython-36.pyc'])],
    ),
])
def test_check_W001(rows, failures):
    """
    Check if the test tasks.

    Args:
        rows: (int): write your description
        failures: (todo): write your description
    """
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    whlcon.add_record_rows(rows)
    whlcon.validate_tree()
    checker = WheelChecker()
    assert checker.check_W001(whlcon) == failures

@pytest.mark.parametrize('rows,failures', [
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=UxbST6sF1RzAkvG8kCt15x13QBsB5FPeLnRJ4wHMqps',
                '1003',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4',
                '995',
            ],
            [
                'foo/__init__.py',
                'sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU',
                '0',
            ],
            [
                'foo/duplicate.py',
                'sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4',
                '995',
            ],
        ],
        [FailedCheck(Check.W002, ['foo.py', 'foo/duplicate.py'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo/__init__.py',
                'sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU',
                '0',
            ],
            [
                'foo/bar.py',
                'sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4',
                '995',
            ],
            [
                'foo/baz/__init__.py',
                'sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU',
                '0',
            ],
            [
                'foo/baz/glarch.py',
                'sha256=m3wA6iovIgZaLZYr_xrE8iSsa_LuKNeaXihzIV4uyMk',
                '973',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo/__init__.py',
                'sha256=iwhKnzeBJLKxpRVjvzwiRE63_zNpIBfaKLITauVph-0',
                '24',
            ],
            [
                'foo/bar.py',
                'sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4',
                '995',
            ],
            [
                'foo/baz/__init__.py',
                'sha256=iwhKnzeBJLKxpRVjvzwiRE63_zNpIBfaKLITauVph-0',
                '24',
            ],
            [
                'foo/baz/glarch.py',
                'sha256=m3wA6iovIgZaLZYr_xrE8iSsa_LuKNeaXihzIV4uyMk',
                '973',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4',
                '995',
            ],
            [
                'foo/__init__.py',
                'sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU',
                '0',
            ],
            [
                'foo/duplicate.py',
                'sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4',
                '995',
            ],
            [
                'foo/bar.py',
                'sha256=D43B5klhA1Tiklczo1UwVmIPeprAw3XTE5p4VdeJIHs',
                '1007',
            ],
            [
                'foo/another_duplicate.py',
                'sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4',
                '995',
            ],
        ],
        [FailedCheck(
            Check.W002, [
                'foo.py',
                'foo/duplicate.py',
                'foo/another_duplicate.py',
            ]
        )],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.dist-info/LICENSE',
                'sha256=oVov1f8LxBN1tMMdn93JEkqCNaMTunicL391TsKTYs8',
                '1012',
            ],
            [
                'foo-1.0.dist-info/NOTICE.txt',
                'sha256=oVov1f8LxBN1tMMdn93JEkqCNaMTunicL391TsKTYs8',
                '1012',
            ],
            [
                'foo.py',
                'sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4',
                '995',
            ],
            [
                'foo/__init__.py',
                'sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU',
                '0',
            ],
            [
                'foo/duplicate.py',
                'sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4',
                '995',
            ],
        ],
        [
            FailedCheck(Check.W002, [
                'foo-1.0.dist-info/LICENSE',
                'foo-1.0.dist-info/NOTICE.txt',
            ]),
            FailedCheck(Check.W002, ['foo.py', 'foo/duplicate.py']),
        ],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo/__init__.py',
                'sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU',
                '0',
            ],
            [
                'foo/__main__.py',
                'sha256=tQnRYEpcEVliJvvWU8Y4pAoe9rl1NqH6YJQuuPgXmtQ',
                '1000',
            ],
            [
                'foo-1.0.data/scripts/command',
                'sha256=tQnRYEpcEVliJvvWU8Y4pAoe9rl1NqH6YJQuuPgXmtQ',
                '1000',
            ],
        ],
        [FailedCheck(Check.W002, ['foo/__main__.py', 'foo-1.0.data/scripts/command'])],
    ),
])
def test_check_W002(rows, failures):
    """
    Check that all tasks have the same wayures have the same.

    Args:
        rows: (int): write your description
        failures: (str): write your description
    """
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    whlcon.add_record_rows(rows)
    whlcon.validate_tree()
    checker = WheelChecker()
    assert checker.check_W002(whlcon) == failures

@pytest.mark.parametrize('rows,failures', [
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'weirdo.txt/notpython.c',
                'sha256=uM5dhqqW1Q9XRVLKeb-4X4L_TIDGeAcRv76WSPB89Ww',
                '1018',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.pth',
                'sha256=qJv4qqYRXYmgIYGR7wCminLSwqTi3BGXKCF52RCOgdo',
                '1021',
            ],
            [
                'foo.py',
                'sha256=vpmJZmgO7hdCay0ocZ8pWruXRPJZNn9fc21GM-D2x7c',
                '1008',
            ],
            [
                'foo.so',
                'sha256=xXxhmk9ydC6QiuOY1VtBIzPFvHyheWbei8vPnYix8GM',
                '1056',
            ],
            [
                'foo.cpython-38-x86_64-linux-gnu.so',
                'sha256=Gx9d_43XJ29NhSx2nVHTrh1VGb1WErVb5ccAu1AmquM',
                '1001',
            ],
            [
                'foo.cpython-38-darwin.so',
                'sha256=_-z_VPLE1qjb5EYEXrcRPLgqvt0hQIk9bQ-u6hBHPiA',
                '1003',
            ],
            [
                'foo.cp38-win_amd64.pyd',
                'sha256=yjQMawGKaU2AOLXp5eDP0hezAIwOb622NVbefwrSpl4',
                '981',
            ],
            [
                'foo.abi3.so',
                'sha256=Sb08Ev4toYT1wHdLPIyZpUKap4DKXxn1jRkCRa2oQ7Y',
                '1011',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/platlib/foo.pth',
                'sha256=qJv4qqYRXYmgIYGR7wCminLSwqTi3BGXKCF52RCOgdo',
                '1021',
            ],
            [
                'foo-1.0.data/platlib/foo.py',
                'sha256=vpmJZmgO7hdCay0ocZ8pWruXRPJZNn9fc21GM-D2x7c',
                '1008',
            ],
            [
                'foo-1.0.data/platlib/foo.so',
                'sha256=xXxhmk9ydC6QiuOY1VtBIzPFvHyheWbei8vPnYix8GM',
                '1056',
            ],
            [
                'foo-1.0.data/platlib/foo.cpython-38-x86_64-linux-gnu.so',
                'sha256=Gx9d_43XJ29NhSx2nVHTrh1VGb1WErVb5ccAu1AmquM',
                '1001',
            ],
            [
                'foo-1.0.data/platlib/foo.cpython-38-darwin.so',
                'sha256=_-z_VPLE1qjb5EYEXrcRPLgqvt0hQIk9bQ-u6hBHPiA',
                '1003',
            ],
            [
                'foo-1.0.data/platlib/foo.cp38-win_amd64.pyd',
                'sha256=yjQMawGKaU2AOLXp5eDP0hezAIwOb622NVbefwrSpl4',
                '981',
            ],
            [
                'foo-1.0.data/platlib/foo.abi3.so',
                'sha256=Sb08Ev4toYT1wHdLPIyZpUKap4DKXxn1jRkCRa2oQ7Y',
                '1011',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            ['empty/', '', ''],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.PY',
                'sha256=dhuWn_iudKMe4a1qeEPOPNAcq3Whv7mJ49yrBnB7HcI',
                '993',
            ],
            [
                'foo.py',
                'sha256=sZ-aaDjmPLqvoNGsEOJGlLle9-azfizy8Mor12ySYjM',
                '994',
            ],
            [
                'foo.pyc',
                'sha256=lyW9ns80fb6JhNHkuySrZEXEfpQK-OPceqelEzvlqME',
                '990',
            ],
            [
                'foo.pyo',
                'sha256=mtnrRZK1tVrhURyT-KWnHR-lq7kHQaPVgJ5Xqn48Rr0',
                '1018',
            ],
        ],
        [FailedCheck(Check.W003, ['foo.PY', 'foo.pyc', 'foo.pyo'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'bar/foo.PY',
                'sha256=dhuWn_iudKMe4a1qeEPOPNAcq3Whv7mJ49yrBnB7HcI',
                '993',
            ],
            [
                'bar/foo.py',
                'sha256=sZ-aaDjmPLqvoNGsEOJGlLle9-azfizy8Mor12ySYjM',
                '994',
            ],
            [
                'bar/foo.pyc',
                'sha256=lyW9ns80fb6JhNHkuySrZEXEfpQK-OPceqelEzvlqME',
                '990',
            ],
            [
                'bar/foo.pyo',
                'sha256=mtnrRZK1tVrhURyT-KWnHR-lq7kHQaPVgJ5Xqn48Rr0',
                '1018',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/platlib/foo.PY',
                'sha256=dhuWn_iudKMe4a1qeEPOPNAcq3Whv7mJ49yrBnB7HcI',
                '993',
            ],
            [
                'foo-1.0.data/platlib/foo.py',
                'sha256=sZ-aaDjmPLqvoNGsEOJGlLle9-azfizy8Mor12ySYjM',
                '994',
            ],
            [
                'foo-1.0.data/platlib/foo.pyc',
                'sha256=lyW9ns80fb6JhNHkuySrZEXEfpQK-OPceqelEzvlqME',
                '990',
            ],
            [
                'foo-1.0.data/platlib/foo.pyo',
                'sha256=mtnrRZK1tVrhURyT-KWnHR-lq7kHQaPVgJ5Xqn48Rr0',
                '1018',
            ],
        ],
        [
            FailedCheck(
                Check.W003,
                [
                    'foo-1.0.data/platlib/foo.PY',
                    'foo-1.0.data/platlib/foo.pyc',
                    'foo-1.0.data/platlib/foo.pyo',
                ],
            )
        ],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'README.rst',
                'sha256=QgWwDAgQK9FiW5bkkmvcpaNuDzIkcLTuuXawN0LinQk',
                '1067',
            ],
            [
                'METADATA',
                'sha256=zcKvdOplywD3AF7XezhX7t7yjoyOxcOAA8d7wF6yFFM',
                '991',
            ],
            [
                'empty',
                'sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU',
                '0',
            ],
        ],
        [FailedCheck(Check.W003, ['README.rst', 'METADATA', 'empty'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/platlib/README.rst',
                'sha256=QgWwDAgQK9FiW5bkkmvcpaNuDzIkcLTuuXawN0LinQk',
                '1067',
            ],
            [
                'foo-1.0.data/platlib/METADATA',
                'sha256=zcKvdOplywD3AF7XezhX7t7yjoyOxcOAA8d7wF6yFFM',
                '991',
            ],
            [
                'foo-1.0.data/platlib/empty',
                'sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU',
                '0',
            ],
        ],
        [
            FailedCheck(
                Check.W003,
                [
                    'foo-1.0.data/platlib/README.rst',
                    'foo-1.0.data/platlib/METADATA',
                    'foo-1.0.data/platlib/empty'
                ],
            )
        ],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.dist-info/README.rst',
                'sha256=QgWwDAgQK9FiW5bkkmvcpaNuDzIkcLTuuXawN0LinQk',
                '1067',
            ],
            [
                'foo-1.0.dist-info/METADATA2',
                'sha256=zcKvdOplywD3AF7XezhX7t7yjoyOxcOAA8d7wF6yFFM',
                '991',
            ],
            [
                'foo-1.0.dist-info/empty',
                'sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU',
                '0',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/scripts/README.rst',
                'sha256=QgWwDAgQK9FiW5bkkmvcpaNuDzIkcLTuuXawN0LinQk',
                '1067',
            ],
            [
                'foo-1.0.data/scripts/METADATA',
                'sha256=zcKvdOplywD3AF7XezhX7t7yjoyOxcOAA8d7wF6yFFM',
                '991',
            ],
            [
                'foo-1.0.data/scripts/empty',
                'sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU',
                '0',
            ],
        ],
        [],
    ),
])
def test_check_W003(rows, failures):
    """
    Create a test test test test.

    Args:
        rows: (int): write your description
        failures: (todo): write your description
    """
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    whlcon.add_record_rows(rows)
    whlcon.validate_tree()
    checker = WheelChecker()
    assert checker.check_W003(whlcon) == failures

@pytest.mark.parametrize('rows,failures', [
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=vq9emnqzd5y6TfrpJLPoaKP7MtYgrCtZpEYJtAlmjzA',
                '977',
            ],
            [
                'def.py',
                'sha256=16w5b0LggY1E5JSzr8RiblYSctfntlvBk_MwbblnAR4',
                '1020',
            ],
            [
                'has-hyphen.py',
                'sha256=5UWLcouj86q9g2AI1YZ2STVx3LT_CNgx5uLv2U8nVQo',
                '953',
            ],
            [
                'extra.ext.py',
                'sha256=hmOOYpAJpnx7rc7YXe3gKJ5M-UFtXwnI-NvxYep65IE',
                '1046',
            ],
            [
                'bar/__init__.py',
                'sha256=Tc4Qg8oo0p3MDy0PhO5eDQ2oS21KdTh7NvGTQBauiIM',
                '1000',
            ],
            [
                'bar/is.py',
                'sha256=BUVi3mdFcyFeRTfRLm3_1uHTiPta6bwB9pHVXX-WF58',
                '1026',
            ],
            [
                'bar/hyphen-ated.py',
                'sha256=7T2OdDysvP6xhq8LTB-GFQqpJQpEkMCgZCRqJAHX2WE',
                '990',
            ],
            [
                'bar/glarch.quux.py',
                'sha256=0gtM3U7nluQlfskhFBF692Xrnfsm1GvnfEWHK_a-Y0Q',
                '988',
            ],
            [
                'with/foo.py',
                'sha256=2ARFPml6z4PzBriQX0CfsTSYvfqgynS9KKfLmKw-2oI',
                '1026',
            ],
            [
                'in-dir/foo.py',
                'sha256=pC7zKJYnbiF3WnlOmC5tMiiXbPDIUhO6-NRkfyyYSIQ',
                '1020',
            ],
            [
                'in.pkg/foo.py',
                'sha256=yAk2NhE0_RxJT_LvwobQOOYMuCS8WenM2fwAZQa2o08',
                '985',
            ],
        ],
        [
            FailedCheck(
                Check.W004,
                [
                    'def.py',
                    'has-hyphen.py',
                    'extra.ext.py',
                    'bar/is.py',
                    'bar/hyphen-ated.py',
                    'bar/glarch.quux.py',
                    'with/foo.py',
                    'in-dir/foo.py',
                    'in.pkg/foo.py',
                ],
            ),
        ],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/platlib/foo.py',
                'sha256=vq9emnqzd5y6TfrpJLPoaKP7MtYgrCtZpEYJtAlmjzA',
                '977',
            ],
            [
                'foo-1.0.data/platlib/def.py',
                'sha256=16w5b0LggY1E5JSzr8RiblYSctfntlvBk_MwbblnAR4',
                '1020',
            ],
            [
                'foo-1.0.data/platlib/has-hyphen.py',
                'sha256=5UWLcouj86q9g2AI1YZ2STVx3LT_CNgx5uLv2U8nVQo',
                '953',
            ],
            [
                'foo-1.0.data/platlib/extra.ext.py',
                'sha256=hmOOYpAJpnx7rc7YXe3gKJ5M-UFtXwnI-NvxYep65IE',
                '1046',
            ],
            [
                'foo-1.0.data/platlib/bar/__init__.py',
                'sha256=Tc4Qg8oo0p3MDy0PhO5eDQ2oS21KdTh7NvGTQBauiIM',
                '1000',
            ],
            [
                'foo-1.0.data/platlib/bar/is.py',
                'sha256=BUVi3mdFcyFeRTfRLm3_1uHTiPta6bwB9pHVXX-WF58',
                '1026',
            ],
            [
                'foo-1.0.data/platlib/bar/hyphen-ated.py',
                'sha256=7T2OdDysvP6xhq8LTB-GFQqpJQpEkMCgZCRqJAHX2WE',
                '990',
            ],
            [
                'foo-1.0.data/platlib/bar/glarch.quux.py',
                'sha256=0gtM3U7nluQlfskhFBF692Xrnfsm1GvnfEWHK_a-Y0Q',
                '988',
            ],
            [
                'foo-1.0.data/platlib/with/foo.py',
                'sha256=2ARFPml6z4PzBriQX0CfsTSYvfqgynS9KKfLmKw-2oI',
                '1026',
            ],
            [
                'foo-1.0.data/platlib/in-dir/foo.py',
                'sha256=pC7zKJYnbiF3WnlOmC5tMiiXbPDIUhO6-NRkfyyYSIQ',
                '1020',
            ],
            [
                'foo-1.0.data/platlib/in.pkg/foo.py',
                'sha256=yAk2NhE0_RxJT_LvwobQOOYMuCS8WenM2fwAZQa2o08',
                '985',
            ],
        ],
        [
            FailedCheck(
                Check.W004,
                [
                    'foo-1.0.data/platlib/def.py',
                    'foo-1.0.data/platlib/has-hyphen.py',
                    'foo-1.0.data/platlib/extra.ext.py',
                    'foo-1.0.data/platlib/bar/is.py',
                    'foo-1.0.data/platlib/bar/hyphen-ated.py',
                    'foo-1.0.data/platlib/bar/glarch.quux.py',
                    'foo-1.0.data/platlib/with/foo.py',
                    'foo-1.0.data/platlib/in-dir/foo.py',
                    'foo-1.0.data/platlib/in.pkg/foo.py',
                ],
            ),
        ],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/scripts/foo.py',
                'sha256=vq9emnqzd5y6TfrpJLPoaKP7MtYgrCtZpEYJtAlmjzA',
                '977',
            ],
            [
                'foo-1.0.data/scripts/def.py',
                'sha256=16w5b0LggY1E5JSzr8RiblYSctfntlvBk_MwbblnAR4',
                '1020',
            ],
            [
                'foo-1.0.data/scripts/has-hyphen.py',
                'sha256=5UWLcouj86q9g2AI1YZ2STVx3LT_CNgx5uLv2U8nVQo',
                '953',
            ],
            [
                'foo-1.0.data/scripts/extra.ext.py',
                'sha256=hmOOYpAJpnx7rc7YXe3gKJ5M-UFtXwnI-NvxYep65IE',
                '1046',
            ],
            [
                'foo-1.0.data/scripts/bar/__init__.py',
                'sha256=Tc4Qg8oo0p3MDy0PhO5eDQ2oS21KdTh7NvGTQBauiIM',
                '1000',
            ],
            [
                'foo-1.0.data/scripts/bar/is.py',
                'sha256=BUVi3mdFcyFeRTfRLm3_1uHTiPta6bwB9pHVXX-WF58',
                '1026',
            ],
            [
                'foo-1.0.data/scripts/bar/hyphen-ated.py',
                'sha256=7T2OdDysvP6xhq8LTB-GFQqpJQpEkMCgZCRqJAHX2WE',
                '990',
            ],
            [
                'foo-1.0.data/scripts/bar/glarch.quux.py',
                'sha256=0gtM3U7nluQlfskhFBF692Xrnfsm1GvnfEWHK_a-Y0Q',
                '988',
            ],
            [
                'foo-1.0.data/scripts/with/foo.py',
                'sha256=2ARFPml6z4PzBriQX0CfsTSYvfqgynS9KKfLmKw-2oI',
                '1026',
            ],
            [
                'foo-1.0.data/scripts/in-dir/foo.py',
                'sha256=pC7zKJYnbiF3WnlOmC5tMiiXbPDIUhO6-NRkfyyYSIQ',
                '1020',
            ],
            [
                'foo-1.0.data/scripts/in.pkg/foo.py',
                'sha256=yAk2NhE0_RxJT_LvwobQOOYMuCS8WenM2fwAZQa2o08',
                '985',
            ],
        ],
        [],
    ),
])
def test_check_W004(rows, failures):
    """
    Check that the test test set.

    Args:
        rows: (int): write your description
        failures: (str): write your description
    """
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    whlcon.add_record_rows(rows)
    whlcon.validate_tree()
    checker = WheelChecker()
    assert checker.check_W004(whlcon) == failures

@pytest.mark.parametrize('name', COMMON_NAMES)
@pytest.mark.parametrize('rows,failures', [
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                '{}/foo.py',
                'sha256=ywELOYVsxhuCagPFoIizTjrI2kux_TxojiEPkLbwPII',
                '973',
            ],
            [
                'not_{}/foo.py',
                'sha256=8iGRSxgfqkMEpbEXL0XLDBYnDqzzTy3XAprVrCE1ikM',
                '1022',
            ],
            [
                '{}.py',
                'sha256=geZ-oqjlCmUGBPINcVlDfps60Wqp-3dBl2z4AwxM-7Q',
                '1010',
            ],
        ],
        [FailedCheck(Check.W005, ['{}/'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'quux/{}/foo.py',
                'sha256=ywELOYVsxhuCagPFoIizTjrI2kux_TxojiEPkLbwPII',
                '973',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                '{}',
                'sha256=ywELOYVsxhuCagPFoIizTjrI2kux_TxojiEPkLbwPII',
                '973',
            ],
        ],
        [FailedCheck(Check.W005, ['{}'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/platlib/{}/foo.py',
                'sha256=ywELOYVsxhuCagPFoIizTjrI2kux_TxojiEPkLbwPII',
                '973',
            ],
        ],
        [FailedCheck(Check.W005, ['foo-1.0.data/platlib/{}/'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/scripts/{}/foo.py',
                'sha256=ywELOYVsxhuCagPFoIizTjrI2kux_TxojiEPkLbwPII',
                '973',
            ],
        ],
        [],
    ),
])
def test_check_W005(name, rows, failures):
    """
    Check that a set of the given tasks have the same as_dir.

    Args:
        name: (str): write your description
        rows: (int): write your description
        failures: (str): write your description
    """
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    rows = [[p.format(name), h, s] for p,h,s in rows]
    failures = [
        FailedCheck(f.check, [a.format(name) for a in f.args])
        for f in failures
    ]
    whlcon.add_record_rows(rows)
    whlcon.validate_tree()
    checker = WheelChecker()
    assert checker.check_W005(whlcon) == failures

@pytest.mark.parametrize('rows,failures', [
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                '__init__.py',
                'sha256=WL4d_yliMuBAdHoAh2GpcMHsdi30rIEqLjRNy33bRIo',
                '1003',
            ],
        ],
        [FailedCheck(Check.W006, ['__init__.py'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo/__init__.py',
                'sha256=WL4d_yliMuBAdHoAh2GpcMHsdi30rIEqLjRNy33bRIo',
                '1003',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/platlib/__init__.py',
                'sha256=WL4d_yliMuBAdHoAh2GpcMHsdi30rIEqLjRNy33bRIo',
                '1003',
            ],
        ],
        [FailedCheck(Check.W006, ['foo-1.0.data/platlib/__init__.py'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.dist-info/__init__.py',
                'sha256=WL4d_yliMuBAdHoAh2GpcMHsdi30rIEqLjRNy33bRIo',
                '1003',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/scripts/__init__.py',
                'sha256=WL4d_yliMuBAdHoAh2GpcMHsdi30rIEqLjRNy33bRIo',
                '1003',
            ],
        ],
        [],
    ),
])
def test_check_W006(rows, failures):
    """
    Check that all tasks in the same as tasks.

    Args:
        rows: (int): write your description
        failures: (str): write your description
    """
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    whlcon.add_record_rows(rows)
    whlcon.validate_tree()
    checker = WheelChecker()
    assert checker.check_W006(whlcon) == failures

@pytest.mark.parametrize('rows,failures', [
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
        ],
        [FailedCheck(Check.W007)],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=-E-9iH5EkvYoKweNQX0uClM__aM3QzBWnSFjWxSXWwc',
                '953',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/platlib/foo.py',
                'sha256=-E-9iH5EkvYoKweNQX0uClM__aM3QzBWnSFjWxSXWwc',
                '953',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/platlib/',
                '',
                '',
            ],
        ],
        [FailedCheck(Check.W007)],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/scripts/foo.py',
                'sha256=UrFRSezsUAirug-a-07CbxceHYeB6n80vcHTJl6YGbo',
                '1031',
            ],
        ],
        [FailedCheck(Check.W007)],
    ),
])
def test_check_W007(rows, failures):
    """
    Check if the test versions.

    Args:
        rows: (int): write your description
        failures: (str): write your description
    """
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    whlcon.add_record_rows(rows)
    whlcon.validate_tree()
    checker = WheelChecker()
    assert checker.check_W007(whlcon) == failures

@pytest.mark.parametrize('rows,failures', [
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
        ],
        [FailedCheck(Check.W008)],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=-E-9iH5EkvYoKweNQX0uClM__aM3QzBWnSFjWxSXWwc',
                '953',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/platlib/foo.py',
                'sha256=-E-9iH5EkvYoKweNQX0uClM__aM3QzBWnSFjWxSXWwc',
                '953',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/platlib/',
                '',
                '',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/scripts/foo.py',
                'sha256=UrFRSezsUAirug-a-07CbxceHYeB6n80vcHTJl6YGbo',
                '1031',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.dist-info/foo.py',
                'sha256=UrFRSezsUAirug-a-07CbxceHYeB6n80vcHTJl6YGbo',
                '1031',
            ],
        ],
        [FailedCheck(Check.W008)],
    ),
])
def test_check_W008(rows, failures):
    """
    Check that all the rows.

    Args:
        rows: (int): write your description
        failures: (todo): write your description
    """
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    whlcon.add_record_rows(rows)
    whlcon.validate_tree()
    checker = WheelChecker()
    assert checker.check_W008(whlcon) == failures

@pytest.mark.parametrize('rows,failures', [
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
                '1027',
            ],
            [
                'bar/__init__.py',
                'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
                '1038',
            ],
        ],
        [FailedCheck(Check.W009, ['foo.py', 'bar/'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
                '1027',
            ],
            [
                'foo-1.0.data/platlib/bar/__init__.py',
                'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
                '1038',
            ],
        ],
        [FailedCheck(Check.W009, ['foo.py', 'foo-1.0.data/platlib/bar/'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
                '1027',
            ],
            [
                'bar/nonpython.txt',
                'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
                '1038',
            ],
        ],
        [FailedCheck(Check.W009, ['foo.py', 'bar/'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
                '1027',
            ],
            [
                '_bar/__init__.py',
                'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
                '1038',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
                '1027',
            ],
            [
                'bar.pth',
                'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
                '1038',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
                '1027',
            ],
            [
                'bar.rst',
                'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
                '1038',
            ],
        ],
        [FailedCheck(Check.W009, ['foo.py', 'bar.rst'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                '_foo.py',
                'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
                '1027',
            ],
            [
                'foo-1.0.data/platlib/bar.py',
                'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
                '1038',
            ],
        ],
        [],
    ),
])
def test_check_W009(rows, failures):
    """
    Check that the test set.

    Args:
        rows: (int): write your description
        failures: (str): write your description
    """
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    whlcon.add_record_rows(rows)
    whlcon.validate_tree()
    checker = WheelChecker()
    assert checker.check_W009(whlcon) == failures

@pytest.mark.parametrize('rows', [
    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'bar/__init__.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'baz/__init__.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'foo-1.0.data/platlib/bar/__init__.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'bar/nonpython.txt',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            '_bar/__init__.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'bar.pth',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'bar.rst',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            '_foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'foo-1.0.data/platlib/bar.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],
])
def test_check_W009_toplevel_set(rows):
    """
    Determine the set.

    Args:
        rows: (todo): write your description
    """
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    whlcon.add_record_rows(rows)
    whlcon.validate_tree()
    checker = WheelChecker()
    checker.configure_options(toplevel=['foo.py', 'bar'])
    assert checker.check_W009(whlcon) == []

@pytest.mark.parametrize('rows', [
    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'bar/__init__.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'baz/__init__.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'foo-1.0.data/platlib/bar/__init__.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'bar/nonpython.txt',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            '_bar/__init__.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'bar.pth',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'bar.rst',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            '_foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'foo-1.0.data/platlib/bar.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],
])
def test_check_W009_pkgtree_set(rows):
    """
    Check if the package packages have a package set.

    Args:
        rows: (todo): write your description
    """
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    whlcon.add_record_rows(rows)
    whlcon.validate_tree()
    checker = WheelChecker(pkgtree=Directory())
    assert checker.check_W009(whlcon) == []

@pytest.mark.parametrize('rows,failures', [
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo/README.txt',
                'sha256=T3ELvA2cR6W39h69EDX-x3IjY6I3VVIv65XltYRPwPU',
                '1014',
            ],
        ],
        [FailedCheck(Check.W010, ['foo/'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/platlib/foo/README.txt',
                'sha256=T3ELvA2cR6W39h69EDX-x3IjY6I3VVIv65XltYRPwPU',
                '1014',
            ],
        ],
        [FailedCheck(Check.W010, ['foo-1.0.data/platlib/foo/'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/data/foo/README.txt',
                'sha256=T3ELvA2cR6W39h69EDX-x3IjY6I3VVIv65XltYRPwPU',
                '1014',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.txt',
                'sha256=T3ELvA2cR6W39h69EDX-x3IjY6I3VVIv65XltYRPwPU',
                '1014',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo/foo.txt',
                'sha256=T3ELvA2cR6W39h69EDX-x3IjY6I3VVIv65XltYRPwPU',
                '1014',
            ],
            [
                'foo/__init__.py',
                'sha256=WI5p9E-mnBVtclEZmTqXLaN9jKCnjQqEitD51Jxo0Cg',
                '1034',
            ],
            [
                'foo/bar/data.dat',
                'sha256=ynvumLLdfyomZOBWkgjjenlaZGTLxDHmzHyaCBw2GDc',
                '981',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo/bar/',
                '',
                '',
            ],
        ],
        [FailedCheck(Check.W010, ['foo/'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo/bar.pyi',
                'sha256=PtaxheMY_aFHWsKvcPeKZuLTfWAbHQaKPe5PWzXzt30',
                '1082',
            ],
        ],
        [FailedCheck(Check.W010, ['foo/'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-stubs/bar.pyi',
                'sha256=PtaxheMY_aFHWsKvcPeKZuLTfWAbHQaKPe5PWzXzt30',
                '1082',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                '-stubs/bar.pyi',
                'sha256=PtaxheMY_aFHWsKvcPeKZuLTfWAbHQaKPe5PWzXzt30',
                '1082',
            ],
        ],
        [FailedCheck(Check.W010, ['-stubs/'])],
    ),
])
def test_check_W010(rows, failures):
    """
    Check that the test set.

    Args:
        rows: (int): write your description
        failures: (todo): write your description
    """
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    whlcon.add_record_rows(rows)
    whlcon.validate_tree()
    checker = WheelChecker()
    assert checker.check_W010(whlcon) == failures

@pytest.mark.parametrize('rows', [
    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'bar/__init__.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'baz/__init__.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'foo-1.0.data/platlib/bar/__init__.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'bar/nonpython.txt',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            '_bar/__init__.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'bar.pth',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'bar.rst',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            '_foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'foo-1.0.data/platlib/bar.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],
])
@pytest.mark.parametrize('check_method', [
    WheelChecker.check_W101,
    WheelChecker.check_W102,
])
def test_check_W1_pkgtree_not_set(rows, check_method):
    """
    Check if the set of packages have the same packages.

    Args:
        rows: (todo): write your description
        check_method: (bool): write your description
    """
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    whlcon.add_record_rows(rows)
    whlcon.validate_tree()
    checker = WheelChecker()
    assert check_method(checker, whlcon) == []

@pytest.mark.parametrize('rows,failures', [
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=yBBAl1_ftr9plr42R3XzaLNykb0avFp3t6zltkR0aEk',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=iHeh5vg23h3ZJ1rVp7dU735mOYUiawTzdrKYYIA6LaM',
                '1031',
            ],
            [
                'bar/bar.py',
                'sha256=tomudU9PWF3CjEtEvpcYDIpLoxIbDfB4qFWqmbP079c',
                '991',
            ],
            [
                'bar/empty/',
                '',
                '',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=yBBAl1_ftr9plr42R3XzaLNykb0avFp3t6zltkR0aEk',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=iHeh5vg23h3ZJ1rVp7dU735mOYUiawTzdrKYYIA6LaM',
                '1031',
            ],
            [
                'bar/bar.py',
                'sha256=tomudU9PWF3CjEtEvpcYDIpLoxIbDfB4qFWqmbP079c',
                '991',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=yBBAl1_ftr9plr42R3XzaLNykb0avFp3t6zltkR0aEk',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=iHeh5vg23h3ZJ1rVp7dU735mOYUiawTzdrKYYIA6LaM',
                '1031',
            ],
            [
                'bar/bar.py',
                'sha256=tomudU9PWF3CjEtEvpcYDIpLoxIbDfB4qFWqmbP079c',
                '991',
            ],
            [
                'extra.py',
                'sha256=UUzLXZ7FFtG2L0HyM9lHdwf4WQfwdkinD8fTIEke5oI',
                '1029',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'bar/__init__.py',
                'sha256=iHeh5vg23h3ZJ1rVp7dU735mOYUiawTzdrKYYIA6LaM',
                '1031',
            ],
            [
                'bar/bar.py',
                'sha256=tomudU9PWF3CjEtEvpcYDIpLoxIbDfB4qFWqmbP079c',
                '991',
            ],
        ],
        [FailedCheck(Check.W101, ['foo.py'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=yBBAl1_ftr9plr42R3XzaLNykb0avFp3t6zltkR0aEk',
                '970',
            ],
        ],
        [FailedCheck(Check.W101, ['bar/__init__.py', 'bar/bar.py'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=yBBAl1_ftr9plr42R3XzaLNykb0avFp3t6zltkR0aEk',
                '970',
            ],
            [
                'foo-1.0.data/platlib/bar/__init__.py',
                'sha256=iHeh5vg23h3ZJ1rVp7dU735mOYUiawTzdrKYYIA6LaM',
                '1031',
            ],
            [
                'foo-1.0.data/platlib/bar/bar.py',
                'sha256=tomudU9PWF3CjEtEvpcYDIpLoxIbDfB4qFWqmbP079c',
                '991',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=yBBAl1_ftr9plr42R3XzaLNykb0avFp3t6zltkR0aEk',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=iHeh5vg23h3ZJ1rVp7dU735mOYUiawTzdrKYYIA6LaM',
                '1031',
            ],
            [
                'foo-1.0.data/platlib/bar/bar.py',
                'sha256=tomudU9PWF3CjEtEvpcYDIpLoxIbDfB4qFWqmbP079c',
                '991',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/platlib/foo.py',
                'sha256=yBBAl1_ftr9plr42R3XzaLNykb0avFp3t6zltkR0aEk',
                '970',
            ],
            [
                'foo-1.0.data/platlib/bar/__init__.py',
                'sha256=iHeh5vg23h3ZJ1rVp7dU735mOYUiawTzdrKYYIA6LaM',
                '1031',
            ],
            [
                'foo-1.0.data/platlib/bar/bar.py',
                'sha256=tomudU9PWF3CjEtEvpcYDIpLoxIbDfB4qFWqmbP079c',
                '991',
            ],
        ],
        [],
    ),
])
def test_check_W101(rows, failures):
    """
    Check that the test files.

    Args:
        rows: (int): write your description
        failures: (todo): write your description
    """
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    whlcon.add_record_rows(rows)
    whlcon.validate_tree()
    checker = WheelChecker(
        pkgtree=Directory(
            path=None,
            entries={
                "foo.py": File(('foo.py',), None, None),
                "bar": Directory(
                    path="bar/",
                    entries={
                        "__init__.py": File(('bar', '__init__.py'), None, None),
                        "bar.py": File(('bar', 'bar.py'), None, None),
                        "empty": Directory(path='bar/empty/'),
                    }
                ),
            },
        ),
    )
    assert checker.check_W101(whlcon) == failures

@pytest.mark.parametrize('rows,failures', [
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=yBBAl1_ftr9plr42R3XzaLNykb0avFp3t6zltkR0aEk',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=iHeh5vg23h3ZJ1rVp7dU735mOYUiawTzdrKYYIA6LaM',
                '1031',
            ],
            [
                'bar/bar.py',
                'sha256=tomudU9PWF3CjEtEvpcYDIpLoxIbDfB4qFWqmbP079c',
                '991',
            ],
            [
                'bar/empty/',
                '',
                '',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=yBBAl1_ftr9plr42R3XzaLNykb0avFp3t6zltkR0aEk',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=iHeh5vg23h3ZJ1rVp7dU735mOYUiawTzdrKYYIA6LaM',
                '1031',
            ],
            [
                'bar/bar.py',
                'sha256=tomudU9PWF3CjEtEvpcYDIpLoxIbDfB4qFWqmbP079c',
                '991',
            ],
            [
                'empty/',
                '',
                '',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=yBBAl1_ftr9plr42R3XzaLNykb0avFp3t6zltkR0aEk',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=iHeh5vg23h3ZJ1rVp7dU735mOYUiawTzdrKYYIA6LaM',
                '1031',
            ],
            [
                'bar/bar.py',
                'sha256=tomudU9PWF3CjEtEvpcYDIpLoxIbDfB4qFWqmbP079c',
                '991',
            ],
            [
                'quux.py',
                'sha256=LK6EWFtHm0hm07tshME9CVuC3kf14vdCbtKV99lhY3o',
                '1047',
            ],
        ],
        [FailedCheck(Check.W102, ['quux.py'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=yBBAl1_ftr9plr42R3XzaLNykb0avFp3t6zltkR0aEk',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=iHeh5vg23h3ZJ1rVp7dU735mOYUiawTzdrKYYIA6LaM',
                '1031',
            ],
            [
                'bar/bar.py',
                'sha256=tomudU9PWF3CjEtEvpcYDIpLoxIbDfB4qFWqmbP079c',
                '991',
            ],
            [
                'bar/quux.py',
                'sha256=LK6EWFtHm0hm07tshME9CVuC3kf14vdCbtKV99lhY3o',
                '1047',
            ],
        ],
        [FailedCheck(Check.W102, ['bar/quux.py'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=yBBAl1_ftr9plr42R3XzaLNykb0avFp3t6zltkR0aEk',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=iHeh5vg23h3ZJ1rVp7dU735mOYUiawTzdrKYYIA6LaM',
                '1031',
            ],
            [
                'bar/bar.py',
                'sha256=tomudU9PWF3CjEtEvpcYDIpLoxIbDfB4qFWqmbP079c',
                '991',
            ],
            [
                'foo-1.0.data/platlib/quux.py',
                'sha256=LK6EWFtHm0hm07tshME9CVuC3kf14vdCbtKV99lhY3o',
                '1047',
            ],
        ],
        [FailedCheck(Check.W102, ['foo-1.0.data/platlib/quux.py'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=yBBAl1_ftr9plr42R3XzaLNykb0avFp3t6zltkR0aEk',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=iHeh5vg23h3ZJ1rVp7dU735mOYUiawTzdrKYYIA6LaM',
                '1031',
            ],
            [
                'bar/bar.py',
                'sha256=tomudU9PWF3CjEtEvpcYDIpLoxIbDfB4qFWqmbP079c',
                '991',
            ],
            [
                'foo.pyc',
                'sha256=LK6EWFtHm0hm07tshME9CVuC3kf14vdCbtKV99lhY3o',
                '1047',
            ],
        ],
        [FailedCheck(Check.W102, ['foo.pyc'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=yBBAl1_ftr9plr42R3XzaLNykb0avFp3t6zltkR0aEk',
                '970',
            ],
            [
                'foo-1.0.data/scripts/quux.py',
                'sha256=BdobLd1HvMLfPVg7de6NHrPKOpiOzrbK3R5hRBruWCs',
                '1010',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=yBBAl1_ftr9plr42R3XzaLNykb0avFp3t6zltkR0aEk',
                '970',
            ],
            [
                'foo-1.0.dist-info/quux.py',
                'sha256=BdobLd1HvMLfPVg7de6NHrPKOpiOzrbK3R5hRBruWCs',
                '1010',
            ],
        ],
        [],
    ),
])
def test_check_W102(rows, failures):
    """
    Create a checker package.

    Args:
        rows: (int): write your description
        failures: (str): write your description
    """
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    whlcon.add_record_rows(rows)
    whlcon.validate_tree()
    checker = WheelChecker(
        pkgtree=Directory(
            path=None,
            entries={
                "foo.py": File(('foo.py',), None, None),
                "bar": Directory(
                    path="bar/",
                    entries={
                        "__init__.py": File(('bar', '__init__.py'), None, None),
                        "bar.py": File(('bar', 'bar.py'), None, None),
                        "empty": Directory(path='bar/empty/'),
                    }
                ),
            },
        ),
    )
    assert checker.check_W102(whlcon) == failures

@pytest.mark.parametrize('rows', [
    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'bar/__init__.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'baz/__init__.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'foo-1.0.data/platlib/bar/__init__.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'bar/nonpython.txt',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            '_bar/__init__.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'bar.pth',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'bar.rst',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],

    [
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            '_foo.py',
            'sha256=Kj8HcD01txI_5GMsyhQTJTvnmEecGbbCQ7_mW-DvQJw',
            '1027',
        ],
        [
            'foo-1.0.data/platlib/bar.py',
            'sha256=zy4yNJt80A0p-wknpES1PtMEWN_QNZKPEhFDYcBrGBo',
            '1038',
        ],
    ],
])
@pytest.mark.parametrize('check_method', [
    WheelChecker.check_W201,
    WheelChecker.check_W202,
])
def test_check_W2_toplevel_not_set(rows, check_method):
    """
    Determine the set of 2nd set.

    Args:
        rows: (todo): write your description
        check_method: (bool): write your description
    """
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    whlcon.add_record_rows(rows)
    whlcon.validate_tree()
    checker = WheelChecker()
    assert check_method(checker, whlcon) == []

@pytest.mark.parametrize('rows,failures', [
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo/__init__.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
        ],
        [FailedCheck(Check.W201, ['foo.py'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'bar.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
        ],
        [FailedCheck(Check.W201, ['bar'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
        ],
        [FailedCheck(Check.W201, ['bar'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
        ],
        [FailedCheck(Check.W201, ['foo.py'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'baz/__init__.py',
                'sha256=udTbfpYahyhOc6RLrDIiCRRVh-9ekXLYMQsnVaOj6bA',
                '1050',
            ],
        ],
        [FailedCheck(Check.W201, ['bar'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
            [
                'glarch/__init__.py',
                'sha256=3xET_xmcTKU8HMePG0CvLcRK_vC04Vl4s5-jrukfvlk',
                '1030',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'foo-1.0.data/platlib/bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/platlib/foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'foo-1.0.data/platlib/bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'bar',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/scripts/foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
        ],
        [FailedCheck(Check.W201, ['foo.py'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
        ],
        [FailedCheck(Check.W201, ['foo.py', 'bar'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
            [
                'quux.pth',
                'sha256=LrfDZecDtwWe8mhGiJBDNHwMrCi2irqTBS1SN308X2k',
                '991',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
            [
                '_glarch.py',
                'sha256=EqNXHE41LQUE3x_cjqP_bEPDD7xHU-4vTp2bf4NUvz4',
                '1008',
            ],
        ],
        [],
    ),
])
@pytest.mark.parametrize('toplevel', [['foo.py', 'bar'], ['foo.py', 'bar/']])
def test_check_W201(rows, failures, toplevel):
    """
    Check that the test set.

    Args:
        rows: (int): write your description
        failures: (todo): write your description
        toplevel: (todo): write your description
    """
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    whlcon.add_record_rows(rows)
    whlcon.validate_tree()
    checker = WheelChecker()
    checker.configure_options(toplevel=toplevel)
    assert checker.check_W201(whlcon) == failures

@pytest.mark.parametrize('rows,failures', [
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo/__init__.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
        ],
        [FailedCheck(Check.W202, ['foo/'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'bar.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
        ],
        [FailedCheck(Check.W202, ['bar.py'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'baz/__init__.py',
                'sha256=udTbfpYahyhOc6RLrDIiCRRVh-9ekXLYMQsnVaOj6bA',
                '1050',
            ],
        ],
        [FailedCheck(Check.W202, ['baz/'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
            [
                'glarch/__init__.py',
                'sha256=3xET_xmcTKU8HMePG0CvLcRK_vC04Vl4s5-jrukfvlk',
                '1030',
            ],
        ],
        [FailedCheck(Check.W202, ['glarch/'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'foo-1.0.data/platlib/bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/platlib/foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'foo-1.0.data/platlib/bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'bar',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/scripts/foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
            [
                'quux.pth',
                'sha256=LrfDZecDtwWe8mhGiJBDNHwMrCi2irqTBS1SN308X2k',
                '991',
            ],
        ],
        [],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
            [
                '_glarch.py',
                'sha256=EqNXHE41LQUE3x_cjqP_bEPDD7xHU-4vTp2bf4NUvz4',
                '1008',
            ],
        ],
        [FailedCheck(Check.W202, ['_glarch.py'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
            [
                'data.dat',
                'sha256=K-fKbGslLcFYZAtsnd7yUPL_v2WC1VtmziGrXrXaS88',
                '988',
            ],
        ],
        [FailedCheck(Check.W202, ['data.dat'])],
    ),

    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'bar/__init__.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
            [
                'empty/',
                '',
                '',
            ],
        ],
        [FailedCheck(Check.W202, ['empty/'])],
    ),
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo/__init__.py',
                'sha256=5UmJMdxr74EIQSMxK2DGo-lUxaoZjb6g8mooBF9HoYA',
                '970',
            ],
            [
                'bar.py',
                'sha256=fAhVWJ2uWDoiJA7y48jSJez2sh3L174ARIOzAKMG8nU',
                '1032',
            ],
        ],
        [FailedCheck(Check.W202, ['foo/', 'bar.py'])],
    ),
])
@pytest.mark.parametrize('toplevel', [['foo.py', 'bar'], ['foo.py', 'bar/']])
def test_check_W202(rows, failures, toplevel):
    """
    Check the test test test.

    Args:
        rows: (int): write your description
        failures: (todo): write your description
        toplevel: (todo): write your description
    """
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    whlcon.add_record_rows(rows)
    whlcon.validate_tree()
    checker = WheelChecker()
    checker.configure_options(toplevel=toplevel)
    assert checker.check_W202(whlcon) == failures
