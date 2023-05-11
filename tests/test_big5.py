import pytest

from character_encoding_utils import big5
from character_encoding_utils.big5 import Big5Exception


def test_query_chr():
    assert big5.query_chr(0xA140) == '　'
    assert big5.query_chr(0xA246) == '¢'
    assert big5.query_chr(0xA440) == '一'
    assert big5.query_chr(0xB050) == '訐'
    assert big5.query_chr(0xC940) == '乂'
    assert big5.query_chr(0xDF60) == '綃'

    with pytest.raises(Big5Exception) as info:
        big5.query_chr(0xA000)
    assert isinstance(info.value.__cause__, UnicodeDecodeError)
    with pytest.raises(Big5Exception) as info:
        big5.query_chr(0xFFFF)
    assert isinstance(info.value.__cause__, UnicodeDecodeError)


def test_query_code():
    assert big5.query_code('　') == 0xA140
    assert big5.query_code('¢') == 0xA246
    assert big5.query_code('一') == 0xA440
    assert big5.query_code('訐') == 0xB050
    assert big5.query_code('乂') == 0xC940
    assert big5.query_code('綃') == 0xDF60

    with pytest.raises(Big5Exception):
        big5.query_code('abc')
    with pytest.raises(Big5Exception):
        big5.query_code('d')

    with pytest.raises(Big5Exception) as info:
        big5.query_code('가')
    assert isinstance(info.value.__cause__, UnicodeEncodeError)


def test_query_category():
    categories = big5.get_categories()
    assert len(categories) == 3
    assert 'other' in categories
    assert 'level-1' in categories
    assert 'level-2' in categories

    assert big5.query_category('■') == 'other'
    assert big5.query_category('一') == 'level-1'
    assert big5.query_category('乂') == 'level-2'
    assert big5.query_category('A') is None
    assert big5.query_category('가') is None


def test_alphabet():
    alphabet = big5.get_alphabet_other()
    assert len(alphabet) == 408
    for c in alphabet:
        code = big5.query_code(c)
        assert big5.query_chr(code) == c
        assert big5.query_category(c) == 'other'

    alphabet = big5.get_alphabet_level_1()
    assert len(alphabet) == 5401
    for c in alphabet:
        code = big5.query_code(c)
        assert big5.query_chr(code) == c
        assert big5.query_category(c) == 'level-1'

    alphabet = big5.get_alphabet_level_2()
    assert len(alphabet) == 7652
    for c in alphabet:
        code = big5.query_code(c)
        assert big5.query_chr(code) == c
        assert big5.query_category(c) == 'level-2'

    alphabet = big5.get_alphabet()
    assert len(alphabet) == 13461
    for c in alphabet:
        code = big5.query_code(c)
        assert big5.query_chr(code) == c
        assert big5.query_category(c) is not None


def test_count():
    assert big5.get_other_count() == 408
    assert big5.get_level_1_count() == 5401
    assert big5.get_level_2_count() == 7652
    assert big5.get_count() == 13461
