import pytest

from character_encoding_utils import gb2312
from character_encoding_utils.gb2312 import GB2312Exception, GB2312EncodeError, GB2312DecodeError


def test_codec():
    assert gb2312.encode('abc中国') == 'abc中国'.encode('gb2312')
    assert gb2312.decode(b'abc\xd6\xd0\xb9\xfa') == b'abc\xd6\xd0\xb9\xfa'.decode('gb2312')

    with pytest.raises(GB2312EncodeError) as info:
        gb2312.encode('abc가')
    assert info.value.object == '가'
    assert info.value.position == 3
    assert info.value.reason == 'illegal multibyte sequence'

    with pytest.raises(GB2312DecodeError) as info:
        gb2312.decode(b'abc\xd6\xd0\xb9')
    assert info.value.object == b'\xb9'
    assert info.value.position == 5
    assert info.value.reason == 'incomplete multibyte sequence'


def test_query_coord():
    assert gb2312.query_coord('＄') == (1, 71)
    assert gb2312.query_coord('拿') == (36, 35)
    assert gb2312.query_coord('贽') == (74, 62)
    assert gb2312.query_coord('魍') == (87, 45)

    with pytest.raises(GB2312Exception):
        gb2312.query_coord('abc')
    with pytest.raises(GB2312Exception):
        gb2312.query_coord('d')

    with pytest.raises(GB2312Exception) as info:
        gb2312.query_coord('가')
    assert isinstance(info.value.__cause__, GB2312EncodeError)


def test_query_chr():
    assert gb2312.query_chr(1, 79) == '★'
    assert gb2312.query_chr(16, 1) == '啊'
    assert gb2312.query_chr(26, 26) == '汉'
    assert gb2312.query_chr(55, 54) == '字'
    assert gb2312.query_chr(87, 94) == '齄'

    with pytest.raises(GB2312Exception):
        gb2312.query_chr(-1, 50)
    with pytest.raises(GB2312Exception):
        gb2312.query_chr(20, 500)

    with pytest.raises(GB2312Exception) as info:
        gb2312.query_chr(94, 94)
    assert isinstance(info.value.__cause__, GB2312DecodeError)


def test_query_category():
    categories = gb2312.get_categories()
    assert len(categories) == 3
    assert 'other' in categories
    assert 'level-1' in categories
    assert 'level-2' in categories

    assert gb2312.query_category('■') == 'other'
    assert gb2312.query_category('闭') == 'level-1'
    assert gb2312.query_category('踔') == 'level-2'
    assert gb2312.query_category('A') is None
    assert gb2312.query_category('가') is None


def test_alphabet():
    alphabet = gb2312.get_alphabet_other()
    assert len(alphabet) == 682
    for c in alphabet:
        row, col = gb2312.query_coord(c)
        assert gb2312.query_chr(row, col) == c
        assert gb2312.query_category(c) == 'other'

    alphabet = gb2312.get_alphabet_level_1()
    assert len(alphabet) == 3755
    for c in alphabet:
        row, col = gb2312.query_coord(c)
        assert gb2312.query_chr(row, col) == c
        assert gb2312.query_category(c) == 'level-1'

    alphabet = gb2312.get_alphabet_level_2()
    assert len(alphabet) == 3008
    for c in alphabet:
        row, col = gb2312.query_coord(c)
        assert gb2312.query_chr(row, col) == c
        assert gb2312.query_category(c) == 'level-2'

    alphabet = gb2312.get_alphabet()
    assert len(alphabet) == 7445
    for c in alphabet:
        row, col = gb2312.query_coord(c)
        assert gb2312.query_chr(row, col) == c
        assert gb2312.query_category(c) is not None


def test_count():
    assert gb2312.get_other_count() == 682
    assert gb2312.get_level_1_count() == 3755
    assert gb2312.get_level_2_count() == 3008
    assert gb2312.get_count() == 7445


def test_unicode():
    alphabet_other = []
    alphabet_level_1 = []
    alphabet_level_2 = []
    alphabet = []

    for code_point in range(0, 0x10FFFF + 1):
        c = chr(code_point)
        category = gb2312.query_category(c)

        if category == 'other':
            alphabet_other.append(c)
        elif category == 'level-1':
            alphabet_level_1.append(c)
        elif category == 'level-2':
            alphabet_level_2.append(c)

        if category is not None:
            alphabet.append(c)

    assert len(alphabet_other) == gb2312.get_other_count()
    assert len(alphabet_level_1) == gb2312.get_level_1_count()
    assert len(alphabet_level_2) == gb2312.get_level_2_count()
    assert len(alphabet) == gb2312.get_count()
