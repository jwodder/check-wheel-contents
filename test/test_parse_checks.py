import pytest
from   check_wheel_contents.checks import Check, parse_checks_string
from   check_wheel_contents.errors import UserInputError

@pytest.mark.parametrize('s,checks', [
    ('', set()),
    ('W001', {Check.W001}),
    ('W001,W002', {Check.W001, Check.W002}),
    ('W001 , W002', {Check.W001, Check.W002}),
    (',W001 , W002,', {Check.W001, Check.W002}),
    ('W00', {Check.W001, Check.W002, Check.W003, Check.W004, Check.W005,
             Check.W006, Check.W007, Check.W008, Check.W009}),
    ('W', set(Check)),
    ('W, W004', set(Check)),
    ('W004, W', set(Check)),
])
def test_parse_checks_string(s, checks):
    assert parse_checks_string(s) == checks

@pytest.mark.parametrize('s,badbit', [
    ('E001', 'E001'),
    ('W001, W0010', 'W0010'),
    ('W001-W007', 'W001-W007'),
    ('W001 - W007', 'W001 - W007'),
    ('w006', 'w006'),
    ('W9', 'W9'),
    ('W999', 'W999'),
])
def test_parse_checks_string_error(s, badbit):
    with pytest.raises(UserInputError) as excinfo:
        parse_checks_string(s)
    assert str(excinfo.value) == f'Unknown check prefix: {badbit}'
