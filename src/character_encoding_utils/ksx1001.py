
_euc_offset = 0xA0


class KSX1001Exception(Exception):
    pass


def query_chr(row: int, col: int):
    # 'euc_kr' 编码器对字符 'Hangul Filler (0x3164)' 的处理不正确，但是官方开发者竟然认为这不是一个错误
    # 问题详情见： https://github.com/python/cpython/issues/101863
    if row == 4 and col == 52:
        return chr(0x3164)

    if row < 1 or row > 94 or col < 1 or col > 94:
        raise KSX1001Exception(f"'row' and 'col' must between 1 and 94")
    try:
        return bytes([row + _euc_offset, col + _euc_offset]).decode('ksx1001')
    except UnicodeDecodeError as e:
        raise KSX1001Exception(f'ksx1001 char at ({row}, {col}) undefined') from e


def query_coord(c: str) -> tuple[int, int]:
    if len(c) != 1:
        raise KSX1001Exception('Must be one char')
    try:
        encoded = c.encode('ksx1001')
    except UnicodeEncodeError as e:
        raise KSX1001Exception(f"'{c}' not a ksx1001 char") from e
    if len(encoded) == 1:
        raise KSX1001Exception(f"'{c}' is a ascii char")
    row = encoded[0] - _euc_offset
    col = encoded[1] - _euc_offset
    return row, col


def get_categories() -> list[str]:
    return ['other', 'syllable', 'hanja']


def query_category(c: str) -> str | None:
    try:
        row = query_coord(c)[0]
    except KSX1001Exception:
        return None

    if 1 <= row <= 12:
        return 'other'
    elif 16 <= row <= 40:
        return 'syllable'
    elif 42 <= row <= 93:
        return 'hanja'
    else:
        raise AssertionError(f'Impossible row: {row}')


def _get_alphabet_by_rows_between(row_start, row_end) -> list[str]:
    alphabet = []
    for row in range(row_start, row_end + 1):
        for col in range(1, 94 + 1):
            try:
                c = query_chr(row, col)
                alphabet.append(c)
            except KSX1001Exception:
                pass
    return alphabet


_alphabet_other = _get_alphabet_by_rows_between(1, 12)
_alphabet_syllable = _get_alphabet_by_rows_between(16, 40)
_alphabet_hanja = _get_alphabet_by_rows_between(42, 93)
_alphabet = _alphabet_other + _alphabet_syllable + _alphabet_hanja


def get_alphabet_other() -> list[str]:
    return list(_alphabet_other)


def get_alphabet_syllable() -> list[str]:
    return list(_alphabet_syllable)


def get_alphabet_hanja() -> list[str]:
    return list(_alphabet_hanja)


def get_alphabet() -> list[str]:
    return list(_alphabet)


def get_other_count() -> int:
    return len(_alphabet_other)


def get_syllable_count() -> int:
    return len(_alphabet_syllable)


def get_hanja_count() -> int:
    return len(_alphabet_hanja)


def get_count() -> int:
    return len(_alphabet)
