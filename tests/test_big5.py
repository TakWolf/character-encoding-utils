import pytest

from character_encoding_utils import big5
from character_encoding_utils.big5 import Big5Exception, Big5EncodeError, Big5DecodeError


def test_codec():
    assert big5.encode('abc中國') == 'abc中國'.encode('big5')
    assert big5.decode(b'abc\xa4\xa4\xb0\xea') == b'abc\xa4\xa4\xb0\xea'.decode('big5')

    with pytest.raises(Big5EncodeError) as info:
        big5.encode('abc가')
    assert info.value.object == '가'
    assert info.value.position == 3
    assert info.value.reason == 'illegal multibyte sequence'

    with pytest.raises(Big5DecodeError) as info:
        big5.decode(b'abc\xa4\xa4\xb0')
    assert info.value.object == b'\xb0'
    assert info.value.position == 5
    assert info.value.reason == 'incomplete multibyte sequence'

    c = '〸'
    assert ord(c) == 0x3038
    assert big5.decode(big5.encode(c)) == c

    c = '〹'
    assert ord(c) == 0x3039
    assert big5.decode(big5.encode(c)) == c

    c = '〺'
    assert ord(c) == 0x303A
    assert big5.decode(big5.encode(c)) == c

    c = '十'
    assert ord(c) == 0x5341
    assert big5.decode(big5.encode(c)) == c

    c = '卄'
    assert ord(c) == 0x5344
    with pytest.raises(Big5EncodeError):
        big5.encode(c)

    c = '卅'
    assert ord(c) == 0x5345
    assert big5.decode(big5.encode(c)) == c

    c = '／'
    assert ord(c) == 0xFF0F
    assert big5.decode(big5.encode(c)) == c

    c = '＼'
    assert ord(c) == 0xFF3C
    assert big5.decode(big5.encode(c)) == c

    c = '∕'
    assert ord(c) == 0x2215
    assert big5.decode(big5.encode(c)) == c

    c = '﹨'
    assert ord(c) == 0xFE68
    assert big5.decode(big5.encode(c)) == c


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
    assert isinstance(info.value.__cause__, Big5EncodeError)


def test_query_chr():
    assert big5.query_chr(0xA140) == '　'
    assert big5.query_chr(0xA246) == '¢'
    assert big5.query_chr(0xA440) == '一'
    assert big5.query_chr(0xB050) == '訐'
    assert big5.query_chr(0xC940) == '乂'
    assert big5.query_chr(0xDF60) == '綃'

    with pytest.raises(Big5Exception) as info:
        big5.query_chr(0xA000)
    assert isinstance(info.value.__cause__, Big5DecodeError)
    with pytest.raises(Big5Exception) as info:
        big5.query_chr(0xFFFF)
    assert isinstance(info.value.__cause__, Big5DecodeError)


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


def test_unicode():
    alphabet_other = []
    alphabet_level_1 = []
    alphabet_level_2 = []
    alphabet = []

    for code_point in range(0, 0x10FFFF + 1):
        c = chr(code_point)
        category = big5.query_category(c)

        if category == 'other':
            alphabet_other.append(c)
        elif category == 'level-1':
            alphabet_level_1.append(c)
        elif category == 'level-2':
            alphabet_level_2.append(c)

        if category is not None:
            alphabet.append(c)

    assert len(alphabet_other) == big5.get_other_count()
    assert len(alphabet_level_1) == big5.get_level_1_count()
    assert len(alphabet_level_2) == big5.get_level_2_count()
    assert len(alphabet) == big5.get_count()
