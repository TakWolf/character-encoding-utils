import pytest

from character_encoding_utils import shiftjis
from character_encoding_utils.shiftjis import ShiftJISEncodeError, ShiftJISDecodeError


def test_codec():
    assert shiftjis.encode('abc日本') == 'abc日本'.encode('shift-jis')
    assert shiftjis.decode(b'abc\x93\xfa\x96\x7b') == b'abc\x93\xfa\x96\x7b'.decode('shift-jis')

    with pytest.raises(ShiftJISEncodeError) as info:
        shiftjis.encode('abc가')
    assert info.value.object == '가'
    assert info.value.position == 3
    assert info.value.reason == 'illegal multibyte sequence'

    with pytest.raises(ShiftJISDecodeError) as info:
        shiftjis.decode(b'abc\x93\xfa\x96')
    assert info.value.object == b'\x96'
    assert info.value.position == 5
    assert info.value.reason == 'incomplete multibyte sequence'

    with pytest.raises(ShiftJISEncodeError) as info:
        shiftjis.encode('\\')
    assert info.value.object == '\\'
    assert info.value.position == 0
    assert '\\' in info.value.reason
    assert '¥' in info.value.reason

    with pytest.raises(ShiftJISEncodeError) as info:
        shiftjis.encode('~')
    assert info.value.object == '~'
    assert info.value.position == 0
    assert '~' in info.value.reason
    assert '‾' in info.value.reason

    assert shiftjis.decode(shiftjis.encode('¥')) == '¥'
    assert shiftjis.decode(shiftjis.encode('‾')) == '‾'


def test_query_category():
    categories = shiftjis.get_categories()
    assert len(categories) == 5
    assert 'single-byte-ascii-control' in categories
    assert 'single-byte-ascii-printable' in categories
    assert 'single-byte-half-width-katakana' in categories
    assert 'double-byte-other' in categories
    assert 'double-byte-kanji' in categories

    assert shiftjis.query_category('\n') == 'single-byte-ascii-control'
    assert shiftjis.query_category('A') == 'single-byte-ascii-printable'
    assert shiftjis.query_category('ｱ') == 'single-byte-half-width-katakana'
    assert shiftjis.query_category('あ') == 'double-byte-other'
    assert shiftjis.query_category('辻') == 'double-byte-kanji'
    assert shiftjis.query_category('가') is None


def test_alphabet():
    alphabet = shiftjis.get_alphabet_single_byte_ascii_control()
    assert len(alphabet) == 33
    for c in alphabet:
        assert shiftjis.query_category(c) == 'single-byte-ascii-control'

    alphabet = shiftjis.get_alphabet_single_byte_ascii_printable()
    assert len(alphabet) == 95
    for c in alphabet:
        assert shiftjis.query_category(c) == 'single-byte-ascii-printable'

    alphabet = shiftjis.get_alphabet_single_byte_half_width_katakana()
    assert len(alphabet) == 63
    for c in alphabet:
        assert shiftjis.query_category(c) == 'single-byte-half-width-katakana'

    alphabet = shiftjis.get_alphabet_double_byte_other()
    assert len(alphabet) == 524
    for c in alphabet:
        assert shiftjis.query_category(c) == 'double-byte-other'

    alphabet = shiftjis.get_alphabet_double_byte_kanji()
    assert len(alphabet) == 6355
    for c in alphabet:
        assert shiftjis.query_category(c) == 'double-byte-kanji'

    alphabet = shiftjis.get_alphabet()
    assert len(alphabet) == 7070
    for c in alphabet:
        assert shiftjis.query_category(c) is not None


def test_count():
    assert shiftjis.get_single_byte_ascii_control_count() == 33
    assert shiftjis.get_single_byte_ascii_printable_count() == 95
    assert shiftjis.get_single_byte_half_width_katakana_count() == 63
    assert shiftjis.get_double_byte_other_count() == 524
    assert shiftjis.get_double_byte_kanji_count() == 6355
    assert shiftjis.get_count() == 7070


def test_unicode():
    alphabet_single_byte_ascii_control = []
    alphabet_single_byte_ascii_printable = []
    alphabet_single_byte_half_width_katakana = []
    alphabet_double_byte_other = []
    alphabet_double_byte_kanji = []
    alphabet = []

    for code_point in range(0, 0x10FFFF + 1):
        c = chr(code_point)
        category = shiftjis.query_category(c)

        if category == 'single-byte-ascii-control':
            alphabet_single_byte_ascii_control.append(c)
        elif category == 'single-byte-ascii-printable':
            alphabet_single_byte_ascii_printable.append(c)
        elif category == 'single-byte-half-width-katakana':
            alphabet_single_byte_half_width_katakana.append(c)
        elif category == 'double-byte-other':
            alphabet_double_byte_other.append(c)
        elif category == 'double-byte-kanji':
            alphabet_double_byte_kanji.append(c)

        if category is not None:
            alphabet.append(c)

    assert len(alphabet_single_byte_ascii_control) == shiftjis.get_single_byte_ascii_control_count()
    assert len(alphabet_single_byte_ascii_printable) == shiftjis.get_single_byte_ascii_printable_count()
    assert len(alphabet_single_byte_half_width_katakana) == shiftjis.get_single_byte_half_width_katakana_count()
    assert len(alphabet_double_byte_other) == shiftjis.get_double_byte_other_count()
    assert len(alphabet_double_byte_kanji) == shiftjis.get_double_byte_kanji_count()
    assert len(alphabet) == shiftjis.get_count()
