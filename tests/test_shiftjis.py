from character_encoding_utils import shiftjis


def test_codec():
    assert shiftjis.encode('日本') == '日本'.encode('shift-jis')
    assert shiftjis.decode(b'\x93\xfa\x96\x7b') == b'\x93\xfa\x96\x7b'.decode('shift-jis')


def test_query_category():
    categories = shiftjis.get_categories()
    assert len(categories) == 4
    assert 'single-ascii' in categories
    assert 'single-other' in categories
    assert 'double-other' in categories
    assert 'double-kanji' in categories

    assert shiftjis.query_category('A') == 'single-ascii'
    assert shiftjis.query_category('ｱ') == 'single-other'
    assert shiftjis.query_category('あ') == 'double-other'
    assert shiftjis.query_category('辻') == 'double-kanji'
    assert shiftjis.query_category('가') is None


def test_alphabet():
    alphabet = shiftjis.get_alphabet_single_ascii()
    assert len(alphabet) == 95
    for c in alphabet:
        assert shiftjis.query_category(c) == 'single-ascii'

    alphabet = shiftjis.get_alphabet_single_other()
    assert len(alphabet) == 63
    for c in alphabet:
        assert shiftjis.query_category(c) == 'single-other'

    alphabet = shiftjis.get_alphabet_double_other()
    assert len(alphabet) == 524
    for c in alphabet:
        assert shiftjis.query_category(c) == 'double-other'

    alphabet = shiftjis.get_alphabet_double_kanji()
    assert len(alphabet) == 6355
    for c in alphabet:
        assert shiftjis.query_category(c) == 'double-kanji'

    alphabet = shiftjis.get_alphabet()
    assert len(alphabet) == 7037
    for c in alphabet:
        assert shiftjis.query_category(c) is not None


def test_count():
    assert shiftjis.get_single_ascii_count() == 95
    assert shiftjis.get_single_other_count() == 63
    assert shiftjis.get_double_other_count() == 524
    assert shiftjis.get_double_kanji_count() == 6355
    assert shiftjis.get_count() == 7037
