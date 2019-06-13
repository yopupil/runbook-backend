# encoding: utf-8
import pytest


from ..endpoint_uri_utils import *

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


@pytest.mark.unit
@pytest.mark.endpoint_uri_utils
@pytest.mark.parametrize('configs_and_parsed', [
    ('a=1', ('a', '1')),
    ('b=str', ('b', 'str')),
    ('a=', ('a', '')),
    ('b', ('b', None)),
    ('b a=1', ('b_a', '1'))
])
def test_parse_arg_and_default_value(configs_and_parsed):
    assert configs_and_parsed[1] == parse_arg_and_default_value(configs_and_parsed[0])


@pytest.mark.unit
@pytest.mark.endpoint_uri_utils
@pytest.mark.parametrize('args', [
    ('<string:a_1>', {'dataType': str, 'arg': 'a_1', 'defaultValue': None}),
    ('<int:a 1=2>', {'dataType': int, 'arg': 'a_1', 'defaultValue': 2}),
    ('<bool:a 1=2>', {'dataType': bool, 'arg': 'a_1', 'defaultValue': True}),
    ('<bool:a 1=false>', {'dataType': bool, 'arg': 'a_1', 'defaultValue': False})
])
def test_parse_param_config(args):
    assert parse_param_config(args[0]) == args[1]


@pytest.mark.unit
@pytest.mark.endpoint_uri_utils
@pytest.mark.parametrize('input', [
    '<random:a_1>',
    '<:abc>'
])
def test_parse_param_config_wrong_inputs(input):
    with pytest.raises(ValueError):
        parse_param_config(input)


@pytest.mark.unit
@pytest.mark.endpoint_uri_utils
@pytest.mark.parametrize('input', [
    [(None, int), None],
    [('2', int), 2],
    [('true', str), 'true'],
    [(2, str), '2'],
    [('false', bool), False],
    [('False', bool), False],
    [('true', bool), True]
])
def test_typecast_value(input):
    assert typecast_value(*input[0]) == input[1]

@pytest.mark.unit
@pytest.mark.endpoint_uri_utils
@pytest.mark.parametrize('input', [
    ('None', int),
    ('2.1', int)
])
def test_typecast_value_wrong_inputs(input):
    with pytest.raises(ValueError):
        typecast_value(*input)
