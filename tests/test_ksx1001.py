import pytest

from character_encoding_utils import ksx1001
from character_encoding_utils.ksx1001 import KSX1001Exception, KSX1001EncodeError, KSX1001DecodeError


def test_codec():
    assert ksx1001.encode('abc가쳰') == 'abc가쳰'.encode('ksx1001')
    assert ksx1001.decode(b'abc\xb0\xa1\xc3\xc8') == b'abc\xb0\xa1\xc3\xc8'.decode('ksx1001')

    with pytest.raises(KSX1001EncodeError) as info:
        ksx1001.encode('abc😈')
    assert info.value.object == '😈'
    assert info.value.position == 3
    assert info.value.reason == 'illegal multibyte sequence'

    with pytest.raises(KSX1001DecodeError) as info:
        ksx1001.decode(b'abc\xb0\xa1\xc3')
    assert info.value.object == b'\xc3'
    assert info.value.position == 5
    assert info.value.reason == 'incomplete multibyte sequence'

    assert ksx1001.decode(ksx1001.encode(chr(0x3164))) == chr(0x3164)

    for code_point in range(0xAC00, 0xD7A4):
        c = chr(code_point)
        assert ksx1001.decode(ksx1001.encode(c)) == c


def test_query_coord():
    assert ksx1001.query_coord('ㆌ') == (4, 92)
    assert ksx1001.query_coord('φ') == (5, 85)
    assert ksx1001.query_coord('떰') == (22, 22)
    assert ksx1001.query_coord('틘') == (38, 24)
    assert ksx1001.query_coord('紺') == (42, 90)
    assert ksx1001.query_coord('絿') == (47, 29)

    with pytest.raises(KSX1001Exception):
        ksx1001.query_coord('abc')
    with pytest.raises(KSX1001Exception):
        ksx1001.query_coord('d')

    with pytest.raises(KSX1001Exception) as info:
        ksx1001.query_coord('😈')
    assert isinstance(info.value.__cause__, KSX1001EncodeError)


def test_query_chr():
    assert ksx1001.query_chr(1, 50) == '⌒'
    assert ksx1001.query_chr(16, 1) == '가'
    assert ksx1001.query_chr(35, 40) == '쳰'
    assert ksx1001.query_chr(50, 54) == '壟'
    assert ksx1001.query_chr(93, 94) == '詰'

    with pytest.raises(KSX1001Exception):
        ksx1001.query_chr(-1, 50)
    with pytest.raises(KSX1001Exception):
        ksx1001.query_chr(20, 500)

    with pytest.raises(KSX1001Exception) as info:
        ksx1001.query_chr(94, 94)
    assert isinstance(info.value.__cause__, KSX1001DecodeError)


def test_query_category():
    categories = ksx1001.get_categories()
    assert len(categories) == 3
    assert 'other' in categories
    assert 'syllable' in categories
    assert 'hanja' in categories

    assert ksx1001.query_category('ぜ') == 'other'
    assert ksx1001.query_category('룝') == 'syllable'
    assert ksx1001.query_category('絿') == 'hanja'
    assert ksx1001.query_category('A') is None
    assert ksx1001.query_category('😈') is None


def test_alphabet():
    alphabet = ksx1001.get_alphabet_other()
    assert len(alphabet) == 988
    for c in alphabet:
        row, col = ksx1001.query_coord(c)
        assert ksx1001.query_chr(row, col) == c
        assert ksx1001.query_category(c) == 'other'

    alphabet = ksx1001.get_alphabet_syllable()
    assert len(alphabet) == 2350
    for c in alphabet:
        row, col = ksx1001.query_coord(c)
        assert ksx1001.query_chr(row, col) == c
        assert ksx1001.query_category(c) == 'syllable'

    alphabet = ksx1001.get_alphabet_hanja()
    assert len(alphabet) == 4888
    for c in alphabet:
        row, col = ksx1001.query_coord(c)
        assert ksx1001.query_chr(row, col) == c
        assert ksx1001.query_category(c) == 'hanja'

    alphabet = ksx1001.get_alphabet()
    assert len(alphabet) == 8226
    for c in alphabet:
        row, col = ksx1001.query_coord(c)
        assert ksx1001.query_chr(row, col) == c
        assert ksx1001.query_category(c) is not None


def test_count():
    assert ksx1001.get_other_count() == 988
    assert ksx1001.get_syllable_count() == 2350
    assert ksx1001.get_hanja_count() == 4888
    assert ksx1001.get_count() == 8226


def test_unicode():
    alphabet_other = []
    alphabet_syllable = []
    alphabet_hanja = []
    alphabet = []

    for code_point in range(0, 0x10FFFF + 1):
        c = chr(code_point)
        category = ksx1001.query_category(c)

        if category == 'other':
            alphabet_other.append(c)
        elif category == 'syllable':
            alphabet_syllable.append(c)
        elif category == 'hanja':
            alphabet_hanja.append(c)

        if category is not None:
            alphabet.append(c)

    assert len(alphabet_other) == ksx1001.get_other_count()
    assert len(alphabet_syllable) == ksx1001.get_syllable_count()
    assert len(alphabet_hanja) == ksx1001.get_hanja_count()
    assert len(alphabet) == ksx1001.get_count()
