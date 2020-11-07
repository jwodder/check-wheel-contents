from   pathlib                       import Path
import pytest
from   check_wheel_contents.contents import WheelContents
from   check_wheel_contents.errors   import WheelValidationError
from   check_wheel_contents.filetree import Directory, File

WHEEL_DIR = Path(__file__).with_name('data') / 'wheels'

def test_from_wheel_purelib():
    whlcon = WheelContents.from_wheel(
        WHEEL_DIR / 'ttyrec2video-0.1.0.dev1-py3-none-any.whl'
    )
    assert whlcon.dist_info_dir == 'ttyrec2video-0.1.0.dev1.dist-info'
    assert whlcon.data_dir == 'ttyrec2video-0.1.0.dev1.data'
    assert whlcon.root_is_purelib is True
    assert whlcon.filetree == Directory(
        path=None,
        entries={
            "ttyrec2video": Directory(
                path='ttyrec2video/',
                entries={
                    "__init__.py": File(
                        ('ttyrec2video', '__init__.py'),
                        322,
                        'sha256=Hsh34fgmI71Le1sOCameXxLmc01bHIwLd1EczCvLPfk',
                    ),
                    "__main__.py": File(
                        ('ttyrec2video', '__main__.py'),
                        5740,
                        'sha256=Twv8iXPtwJrGSlSnM4iF31heGfNtU0Wc9reUlSVebzE',
                    ),
                    "reader.py": File(
                        ('ttyrec2video', 'reader.py'),
                        1440,
                        'sha256=F29z_79pvjQv3_EXDGqsm47SIsRvRzwr6YlISUSqQrI',
                    ),
                    "renderer.py": File(
                        ('ttyrec2video', 'renderer.py'),
                        3873,
                        'sha256=OWBPDb5D2QXrOW77sCf3RU9BQoJAutMvEcbPuWfE96Q',
                    ),
                    "data": Directory(
                        path="ttyrec2video/data/",
                        entries={
                            "ubuntu-font": Directory(
                                path="ttyrec2video/data/ubuntu-font/",
                                entries={
                                    "LICENCE.txt": File(
                                        ('ttyrec2video', 'data', 'ubuntu-font', 'LICENCE.txt'),
                                        4673,
                                        'sha256=LwAVEI1oYnvXiNMT9SnCH_TaLCxCpeHziDrMg0gPkAI',
                                    ),
                                    "UbuntuMono-B.ttf": File(
                                        ('ttyrec2video', 'data', 'ubuntu-font', 'UbuntuMono-B.ttf'),
                                        191400,
                                        'sha256=EfFcOmu9mYqGlf3vs0dZMcN4mqA111RvLv546Ds1L2s',
                                    ),
                                    "UbuntuMono-R.ttf": File(
                                        ('ttyrec2video', 'data', 'ubuntu-font', 'UbuntuMono-R.ttf'),
                                        205748,
                                        'sha256=s13Z0hMdXYOpuH_prSLGKI-j0XaI1DMCwU2imBJBfWM',
                                    ),
                                    "copyright.txt": File(
                                        ('ttyrec2video', 'data', 'ubuntu-font', 'copyright.txt'),
                                        155,
                                        'sha256=cVepFSJyTOB53fpTOhsQJeMdOyJ-GUz42AFZO6aSkUc',
                                    ),
                                },
                            ),
                        },
                    ),
                },
            ),
            "ttyrec2video-0.1.0.dev1.dist-info": Directory(
                path="ttyrec2video-0.1.0.dev1.dist-info/",
                entries={
                    "LICENSE": File(
                        ("ttyrec2video-0.1.0.dev1.dist-info", 'LICENSE'),
                        1090,
                        'sha256=SDaeT4Cm3ZeLgPOOL_f9BliMMHH_GVwqJa6czCztoS0',
                    ),
                    "METADATA": File(
                        ("ttyrec2video-0.1.0.dev1.dist-info", "METADATA"),
                        6269,
                        'sha256=ygypUvb3Lxe6WESfxHSy4-io4OKIeX4vNFo9i-SHnCs',
                    ),
                    "WHEEL": File(
                        ("ttyrec2video-0.1.0.dev1.dist-info", "WHEEL"),
                        92,
                        'sha256=p46_5Uhzqz6AzeSosiOnxK-zmFja1i22CrQCjmYe8ec',
                    ),
                    "entry_points.txt": File(
                        ("ttyrec2video-0.1.0.dev1.dist-info", "entry_points.txt"),
                        61,
                        'sha256=471F-9Jb_a39olsyfq1Dy9lLnXHzPrlbYFiJM6Z3UJU',
                    ),
                    "top_level.txt": File(
                        ("ttyrec2video-0.1.0.dev1.dist-info", "top_level.txt"),
                        13,
                        'sha256=FPSSfqt5fY1q0yYG27bAcWDPnkWB528v1lZg9meePUw',
                    ),
                    "RECORD": File(
                        ("ttyrec2video-0.1.0.dev1.dist-info", "RECORD"),
                        None,
                        None,
                    ),
                },
            ),
        }
    )
    assert whlcon.by_signature == {
        (322, 'sha256=Hsh34fgmI71Le1sOCameXxLmc01bHIwLd1EczCvLPfk'):
            [whlcon.filetree["ttyrec2video"]["__init__.py"]],
        (5740, 'sha256=Twv8iXPtwJrGSlSnM4iF31heGfNtU0Wc9reUlSVebzE'):
            [whlcon.filetree["ttyrec2video"]["__main__.py"]],
        (1440, 'sha256=F29z_79pvjQv3_EXDGqsm47SIsRvRzwr6YlISUSqQrI'):
            [whlcon.filetree["ttyrec2video"]["reader.py"]],
        (3873, 'sha256=OWBPDb5D2QXrOW77sCf3RU9BQoJAutMvEcbPuWfE96Q'):
            [whlcon.filetree["ttyrec2video"]["renderer.py"]],
        (4673, 'sha256=LwAVEI1oYnvXiNMT9SnCH_TaLCxCpeHziDrMg0gPkAI'):
            [whlcon.filetree["ttyrec2video"]["data"]["ubuntu-font"]["LICENCE.txt"]],
        (191400, 'sha256=EfFcOmu9mYqGlf3vs0dZMcN4mqA111RvLv546Ds1L2s'):
            [whlcon.filetree["ttyrec2video"]["data"]["ubuntu-font"]["UbuntuMono-B.ttf"]],
        (205748, 'sha256=s13Z0hMdXYOpuH_prSLGKI-j0XaI1DMCwU2imBJBfWM'):
            [whlcon.filetree["ttyrec2video"]["data"]["ubuntu-font"]["UbuntuMono-R.ttf"]],
        (155, 'sha256=cVepFSJyTOB53fpTOhsQJeMdOyJ-GUz42AFZO6aSkUc'):
            [whlcon.filetree["ttyrec2video"]["data"]["ubuntu-font"]["copyright.txt"]],
        (1090, 'sha256=SDaeT4Cm3ZeLgPOOL_f9BliMMHH_GVwqJa6czCztoS0'):
            [whlcon.filetree["ttyrec2video-0.1.0.dev1.dist-info"]["LICENSE"]],
        (6269, 'sha256=ygypUvb3Lxe6WESfxHSy4-io4OKIeX4vNFo9i-SHnCs'):
            [whlcon.filetree["ttyrec2video-0.1.0.dev1.dist-info"]["METADATA"]],
        (92, 'sha256=p46_5Uhzqz6AzeSosiOnxK-zmFja1i22CrQCjmYe8ec'):
            [whlcon.filetree["ttyrec2video-0.1.0.dev1.dist-info"]["WHEEL"]],
        (61, 'sha256=471F-9Jb_a39olsyfq1Dy9lLnXHzPrlbYFiJM6Z3UJU'):
            [whlcon.filetree["ttyrec2video-0.1.0.dev1.dist-info"]["entry_points.txt"]],
        (13, 'sha256=FPSSfqt5fY1q0yYG27bAcWDPnkWB528v1lZg9meePUw'):
            [whlcon.filetree["ttyrec2video-0.1.0.dev1.dist-info"]["top_level.txt"]],
        (None, None):
            [whlcon.filetree["ttyrec2video-0.1.0.dev1.dist-info"]["RECORD"]],
    }
    assert whlcon.purelib_tree == Directory(
        path=None,
        entries={"ttyrec2video": whlcon.filetree["ttyrec2video"]},
    )
    assert whlcon.platlib_tree == Directory(
        path='ttyrec2video-0.1.0.dev1.data/platlib/',
        entries={},
    )

def test_from_wheel_normalized_dist_info():
    whlcon = WheelContents.from_wheel(
        WHEEL_DIR / 'NLPTriples-0.1.7-py3-none-any.whl'
    )
    assert whlcon.dist_info_dir == 'nlptriples-0.1.7.dist-info'
    assert whlcon.data_dir == 'NLPTriples-0.1.7.data'
    assert whlcon.root_is_purelib is True
    assert whlcon.filetree == Directory(
        path=None,
        entries={
            "nlptriples": Directory(
                path='nlptriples/',
                entries={
                    "__init__.py": File(
                        ('nlptriples', '__init__.py'),
                        22,
                        'sha256=ls1camlIoMxEZz9gSkZ1OJo-MXqHWwKPtdPbZJmwp7E',
                    ),
                    "parse_tree.py": File(
                        ('nlptriples', 'parse_tree.py'),
                        1344,
                        'sha256=EVaZLOTa-2K88oXy105KFitx1nrkxW5Kj7bNABp_JH4',
                    ),
                    "setup.py": File(
                        ('nlptriples', 'setup.py'),
                        58,
                        'sha256=vYdNPB1dWAxaP0dZzTxFxYHCaeZ2EICCJWsIY26UpOc',
                    ),
                    "triples.py": File(
                        ('nlptriples', 'triples.py'),
                        7765,
                        'sha256=dmwUnDeO9z0nuF3oDiFlKXTjj0XlH9gG3cfo0Z-ylrE',
                    ),
                },
            ),
            "nlptriples-0.1.7.dist-info": Directory(
                path="nlptriples-0.1.7.dist-info/",
                entries={
                    "LICENSE": File(
                        ("nlptriples-0.1.7.dist-info", 'LICENSE'),
                        1070,
                        'sha256=VC7YIze9O5Ts59woVlji8eLn1GDvQCbCAXhG66uWFrE',
                    ),
                    "WHEEL": File(
                        ("nlptriples-0.1.7.dist-info", "WHEEL"),
                        84,
                        'sha256=Q99itqWYDhV793oHzqzi24q7L7Kdiz6cb55YDfTXphE',
                    ),
                    "METADATA": File(
                        ("nlptriples-0.1.7.dist-info", "METADATA"),
                        1603,
                        'sha256=dZ2YtcY8Gx3QiUFNjxqfQ4KRJAydb6-vCb2V0QYGe2U',
                    ),
                    "RECORD": File(
                        ("nlptriples-0.1.7.dist-info", "RECORD"),
                        None,
                        None,
                    ),
                },
            ),
        }
    )
    assert whlcon.by_signature == {
        (22, 'sha256=ls1camlIoMxEZz9gSkZ1OJo-MXqHWwKPtdPbZJmwp7E'):
            [whlcon.filetree["nlptriples"]["__init__.py"]],
        (1344, 'sha256=EVaZLOTa-2K88oXy105KFitx1nrkxW5Kj7bNABp_JH4'):
            [whlcon.filetree["nlptriples"]["parse_tree.py"]],
        (58, 'sha256=vYdNPB1dWAxaP0dZzTxFxYHCaeZ2EICCJWsIY26UpOc'):
            [whlcon.filetree["nlptriples"]["setup.py"]],
        (7765, 'sha256=dmwUnDeO9z0nuF3oDiFlKXTjj0XlH9gG3cfo0Z-ylrE'):
            [whlcon.filetree["nlptriples"]["triples.py"]],
        (1070, 'sha256=VC7YIze9O5Ts59woVlji8eLn1GDvQCbCAXhG66uWFrE'):
            [whlcon.filetree["nlptriples-0.1.7.dist-info"]["LICENSE"]],
        (84, 'sha256=Q99itqWYDhV793oHzqzi24q7L7Kdiz6cb55YDfTXphE'):
            [whlcon.filetree["nlptriples-0.1.7.dist-info"]["WHEEL"]],
        (1603, 'sha256=dZ2YtcY8Gx3QiUFNjxqfQ4KRJAydb6-vCb2V0QYGe2U'):
            [whlcon.filetree["nlptriples-0.1.7.dist-info"]["METADATA"]],
        (None, None):
            [whlcon.filetree["nlptriples-0.1.7.dist-info"]["RECORD"]],
    }
    assert whlcon.purelib_tree == Directory(
        path=None,
        entries={"nlptriples": whlcon.filetree["nlptriples"]},
    )
    assert whlcon.platlib_tree == Directory(
        path='NLPTriples-0.1.7.data/platlib/',
        entries={},
    )

def test_trees_data_platlib():
    """
    Test the ``purelib_tree`` and ``platlib_tree`` attributes of a purelib
    wheel containing an empty purelib and a nonempty platlib
    """
    whlcon = WheelContents.from_wheel(WHEEL_DIR/'MPC2860-0.3-py3-none-any.whl')
    assert whlcon.dist_info_dir == 'MPC2860-0.3.dist-info'
    assert whlcon.data_dir == 'MPC2860-0.3.data'
    assert whlcon.root_is_purelib is True
    assert whlcon.purelib_tree == Directory()
    assert whlcon.platlib_tree == Directory(
        path='MPC2860-0.3.data/platlib/',
        entries={
            "_motion_2860.pyd": File(
                ('MPC2860-0.3.data', 'platlib', '_motion_2860.pyd'),
                23040,
                'sha256=kCCzhKz-ZujN2OI0gaeB1W1WHUaC_PdifaIwy4AG6uA',
            ),
            "MPC2860": Directory(
                path='MPC2860-0.3.data/platlib/MPC2860/',
                entries={
                    "MPC2860.dll": File(
                        ('MPC2860-0.3.data', 'platlib', 'MPC2860', 'MPC2860.dll'),
                        548974,
                        'sha256=kOatNp1OqMU-bSzDgNtl9fg-cbQROp2pfnC_dAkD7zw',
                    ),
                    "MPC2860.lib": File(
                        ('MPC2860-0.3.data', 'platlib', 'MPC2860', 'MPC2860.lib'),
                        29200,
                        'sha256=mW1wenQt2kDLZLZFNShxzTxI-lsFUvroi7nlOC-WnbA',
                    ),
                    "MPC2860CFG.txt": File(
                        ('MPC2860-0.3.data', 'platlib', 'MPC2860', 'MPC2860CFG.txt'),
                        56,
                        'sha256=HVDtq-6twa1_nOtCBmuyrGB24EsnJ8PmoRYdqqBqFDI',
                    ),
                    "__init__.py": File(
                        ('MPC2860-0.3.data', 'platlib', 'MPC2860', '__init__.py'),
                        27,
                        'sha256=PYXKN_qL7Q0aak8GkOsleT-8hAezfzcbRR3gxCSB7n8',
                    ),
                    "_motion_2860.pyd": File(
                        ('MPC2860-0.3.data', 'platlib', 'MPC2860', '_motion_2860.pyd'),
                        23040,
                        'sha256=kCCzhKz-ZujN2OI0gaeB1W1WHUaC_PdifaIwy4AG6uA',
                    ),
                    "motion_2860.i": File(
                        ('MPC2860-0.3.data', 'platlib', 'MPC2860', 'motion_2860.i'),
                        98,
                        'sha256=cwWUHTvpo_ZmeSg7pDcD0qUM4LJnuOH2gZS6Zz4f0p8',
                    ),
                    "motion_2860.py": File(
                        ('MPC2860-0.3.data', 'platlib', 'MPC2860', 'motion_2860.py'),
                        4283,
                        'sha256=gn_45lgJZ1MQqvaBkjSnBJSbZUKmWGMy-1G8cln5-78',
                    ),
                },
            ),
        },
    )

def test_trees_data_purelib():
    """
    Test the ``purelib_tree`` and ``platlib_tree`` attributes of a platlib
    wheel containing a nonempty purelib and an empty platlib
    """
    whlcon = WheelContents.from_wheel(
        WHEEL_DIR / 'mxnet_coreml_converter-0.1.0a7-cp27-cp27m-macosx_10_7_x86_64.whl'
    )
    assert whlcon.dist_info_dir == 'mxnet_coreml_converter-0.1.0a7.dist-info'
    assert whlcon.data_dir == 'mxnet_coreml_converter-0.1.0a7.data'
    assert whlcon.root_is_purelib is False
    assert whlcon.purelib_tree == Directory(
        path='mxnet_coreml_converter-0.1.0a7.data/purelib/',
        entries={
            "converter": Directory(
                path='mxnet_coreml_converter-0.1.0a7.data/purelib/converter/',
                entries={
                    "__init__.py": File(
                        ('mxnet_coreml_converter-0.1.0a7.data', 'purelib',
                         'converter', '__init__.py'),
                        786,
                        'sha256=EWsEJdqMbVZOBLYEvcci5VgvFEul-nubLnmcMn5MJlI',
                    ),
                    "_add_pooling.py": File(
                        ('mxnet_coreml_converter-0.1.0a7.data', 'purelib',
                         'converter', '_add_pooling.py'),
                        5499,
                        'sha256=2wyhzbR60jm1uoMqgb50o7QHb7k5S3qJx3Xh17musnE',
                    ),
                    "_layers.py": File(
                        ('mxnet_coreml_converter-0.1.0a7.data', 'purelib',
                         'converter', '_layers.py'),
                        16133,
                        'sha256=5w5ddYvF9mJv0YFKKcg4AqQPae4dZDYwn2iNyihukhU',
                    ),
                    "_mxnet_converter.py": File(
                        ('mxnet_coreml_converter-0.1.0a7.data', 'purelib',
                         'converter', '_mxnet_converter.py'),
                        8850,
                        'sha256=kPLQxZv_KpuwRO1_gaa8vxhSMoDgNDEVJ-ZVLK02L2E',
                    ),
                    "utils.py": File(
                        ('mxnet_coreml_converter-0.1.0a7.data', 'purelib',
                         'converter', 'utils.py'),
                        2447,
                        'sha256=oa9WWamfXwfNVMcjD0MERh_GeiwFDP9n4gEockPDr7Y',
                    ),
                },
            ),
        },
    )
    assert whlcon.platlib_tree == Directory()

def test_trees_platlib():
    """
    Test the ``purelib_tree`` and ``platlib_tree`` attributes of a platlib
    wheel containing an empty purelib and a nonempty platlib
    """
    whlcon = WheelContents.from_wheel(
        WHEEL_DIR / 'bcrypt-3.1.7-cp38-cp38-win_amd64.whl'
    )
    assert whlcon.dist_info_dir == 'bcrypt-3.1.7.dist-info'
    assert whlcon.data_dir == 'bcrypt-3.1.7.data'
    assert whlcon.root_is_purelib is False
    assert whlcon.purelib_tree == Directory(
        path='bcrypt-3.1.7.data/purelib/',
        entries={},
    )
    assert whlcon.platlib_tree == Directory(
        path=None,
        entries={
            "bcrypt": Directory(
                path="bcrypt/",
                entries={
                    "__about__.py": File(
                        ('bcrypt', '__about__.py'),
                        1296,
                        'sha256=jDmr9vNGIReR9gvahrcAIvOGOFq6Zmo_afmjN1Beb5g',
                    ),
                    "__init__.py": File(
                        ('bcrypt', '__init__.py'),
                        5497,
                        'sha256=sIAkb9VLIbn4fHq_8xO79ndQ1bZ5O8rDO8OSHa5-RYs',
                    ),
                    "_bcrypt.cp38-win_amd64.pyd": File(
                        ('bcrypt', '_bcrypt.cp38-win_amd64.pyd'),
                        30208,
                        'sha256=ALdvcGdNK8O_Ux3njNosbQc_9_5W3zzvb1ShFQCPdDU',
                    ),
                },
            ),
        },
    )

@pytest.mark.parametrize('rows,errmsg', [
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'bar-2.1.dist-info/METADATA',
                'sha256=Hp0yrBJbpg0WJ47VO0t0FRl5Kao7MMLJBy1Wa_NSq-I',
                '1036',
            ],
        ],
        'Wheel contains multiple .dist-info directories in RECORD',
    ),
    (
        [
            [
                'bar-2.1.dist-info/METADATA',
                'sha256=Hp0yrBJbpg0WJ47VO0t0FRl5Kao7MMLJBy1Wa_NSq-I',
                '1036',
            ],
        ],
        ".dist-info directory in RECORD ('bar-2.1.dist-info') does not match"
        " actual directory name ('foo-1.0.dist-info')",
    ),
    ([], 'No .dist-info directory in RECORD'),
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/scripts/run.py',
                'sha256=Hwuj2XrWRKLxCyKPPEO-JjAuYyl7OG-2gIlVUweu99g',
                '1075',
            ],
            [
                'bar-1.0.data/scripts/dothing',
                'sha256=VMbmLzjrA37Y6bIpbFmHG21NJfAxgZ7cDgW6m0tArVk',
                '993',
            ],
        ],
        'Wheel contains multiple .data directories in RECORD',
    ),
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'bar-1.0.data/scripts/dothing',
                'sha256=VMbmLzjrA37Y6bIpbFmHG21NJfAxgZ7cDgW6m0tArVk',
                '993',
            ],
        ],
        ".data directory in RECORD ('bar-1.0.data') does not match actual"
        " directory name ('foo-1.0.data')",
    ),
])
@pytest.mark.parametrize('purelib', [True, False])
def test_validate_tree_error(rows, errmsg, purelib):
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=purelib,
    )
    whlcon.add_record_rows(rows)
    with pytest.raises(WheelValidationError) as excinfo:
        whlcon.validate_tree()
    assert str(excinfo.value) == errmsg

@pytest.mark.parametrize('rows,errmsg', [
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/purelib',
                'sha256=ygYxvO8MckoqJYXH20-g3miavH1KhLqYH6hHvW6pQ-k',
                '976',
            ],
        ],
        'Wheel is purelib yet contains *.data/purelib',
    ),
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/purelib/foo.py',
                'sha256=ygYxvO8MckoqJYXH20-g3miavH1KhLqYH6hHvW6pQ-k',
                '976',
            ],
        ],
        'Wheel is purelib yet contains *.data/purelib',
    ),
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/platlib',
                'sha256=ZdniQZSNT-nzhlT2K6hHUMTJe2g9sOYvQf_DLbRzRLw',
                '1015',
            ],
        ],
        '*.data/platlib is not a directory',
    ),
])
def test_validate_tree_error_purelib(rows, errmsg):
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    whlcon.add_record_rows(rows)
    with pytest.raises(WheelValidationError) as excinfo:
        whlcon.validate_tree()
    assert str(excinfo.value) == errmsg

@pytest.mark.parametrize('rows,errmsg', [
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/platlib',
                'sha256=ygYxvO8MckoqJYXH20-g3miavH1KhLqYH6hHvW6pQ-k',
                '976',
            ],
        ],
        'Wheel is platlib yet contains *.data/platlib',
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
                'sha256=ygYxvO8MckoqJYXH20-g3miavH1KhLqYH6hHvW6pQ-k',
                '976',
            ],
        ],
        'Wheel is platlib yet contains *.data/platlib',
    ),
    (
        [
            [
                'foo-1.0.dist-info/METADATA',
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                '950',
            ],
            [
                'foo-1.0.data/purelib',
                'sha256=ZdniQZSNT-nzhlT2K6hHUMTJe2g9sOYvQf_DLbRzRLw',
                '1015',
            ],
        ],
        '*.data/purelib is not a directory',
    ),
])
def test_validate_tree_error_platlib(rows, errmsg):
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=False,
    )
    whlcon.add_record_rows(rows)
    with pytest.raises(WheelValidationError) as excinfo:
        whlcon.validate_tree()
    assert str(excinfo.value) == errmsg

@pytest.mark.parametrize('purelib', [True, False])
def test_validate_tree_data_no_datalib(purelib):
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=purelib,
    )
    whlcon.add_record_rows([
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        [
            'foo-1.0.data/scripts/dothing',
            'sha256=q4OhQ7ORBfBZ2yK5taBaY1uXgH5KmaC7hd9DDWL_IHM',
            '994',
        ],
    ])
    whlcon.validate_tree()

@pytest.mark.parametrize('purelib', [True, False])
def test_validate_tree_dir_rows(purelib):
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=purelib,
    )
    whlcon.add_record_rows([
        [
            'foo-1.0.dist-info/METADATA',
            'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            '950',
        ],
        ['empty/', '', ''],
    ])
    whlcon.validate_tree()
    assert whlcon.filetree == Directory(
        path=None,
        entries={
            "empty": Directory('empty/'),
            "foo-1.0.dist-info": Directory(
                path="foo-1.0.dist-info/",
                entries={
                    "METADATA": File(
                        ('foo-1.0.dist-info', 'METADATA'),
                        950,
                        'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
                    ),
                },
            ),
        },
    )
    assert whlcon.by_signature == {
        (950, 'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk'):
            [whlcon.filetree["foo-1.0.dist-info"]["METADATA"]],
    }

def test_from_wheel_no_purelib_line():
    with pytest.raises(WheelValidationError) as excinfo:
        WheelContents.from_wheel(
            WHEEL_DIR / 'no_purelib_line-1.0.0-py3-none-any.whl'
        )
    assert str(excinfo.value) \
        == 'Root-Is-Purelib header not found in WHEEL file'

def test_from_wheel_empty_purelib_line():
    with pytest.raises(WheelValidationError) as excinfo:
        WheelContents.from_wheel(
            WHEEL_DIR / 'empty_purelib_line-1.0.0-py3-none-any.whl'
        )
    assert str(excinfo.value) \
        == "Invalid Root-Is-Purelib value in WHEEL file: ''"

def test_from_wheel_bad_purelib_line():
    with pytest.raises(WheelValidationError) as excinfo:
        WheelContents.from_wheel(
            WHEEL_DIR / 'bad_purelib_line-1.0.0-py3-none-any.whl'
        )
    assert str(excinfo.value) \
        == "Invalid Root-Is-Purelib value in WHEEL file: 'purelib'"

def test_from_wheel_no_record_file():
    with pytest.raises(WheelValidationError) as excinfo:
        WheelContents.from_wheel(
            WHEEL_DIR / 'no_record-1.0.0-py3-none-any.whl'
        )
    assert str(excinfo.value) == "No RECORD file in wheel"

def test_from_wheel_no_wheel_file():
    with pytest.raises(WheelValidationError) as excinfo:
        WheelContents.from_wheel(
            WHEEL_DIR / 'no_wheel_file-1.0.0-py3-none-any.whl'
        )
    assert str(excinfo.value) == "No WHEEL file in wheel"

def test_by_signature_dup_files():
    whlcon = WheelContents(
        dist_info_dir='foo-1.0.dist-info',
        data_dir='foo-1.0.data',
        root_is_purelib=True,
    )
    whlcon.add_record_rows([
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
    ])
    whlcon.validate_tree()
    assert whlcon.by_signature == {
        (950, 'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk'):
            [File(
                ('foo-1.0.dist-info', 'METADATA'),
                950,
                'sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk',
            )],
        (995, 'sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4'):
            [File(
                ('foo.py',),
                995,
                'sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4',
            ), File(
                ('foo', 'duplicate.py'),
                995,
                'sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4',
            )],
        (0, 'sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU'):
            [File(
                ('foo', '__init__.py'),
                0,
                'sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU',
            )],
    }
