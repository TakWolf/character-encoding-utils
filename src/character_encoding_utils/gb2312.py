
_euc_offset = 0xA0


class GB2312Exception(Exception):
    pass


def query_chr(row: int, col: int) -> str:
    if row < 1 or row > 94 or col < 1 or col > 94:
        raise GB2312Exception(f"'row' and 'col' must between 1 and 94")
    try:
        return bytes([row + _euc_offset, col + _euc_offset]).decode('gb2312')
    except UnicodeDecodeError as e:
        raise GB2312Exception(f'gb2312 char at ({row}, {col}) undefined') from e


def query_coord(c: str) -> tuple[int, int]:
    if len(c) != 1:
        raise GB2312Exception('Must be one char')
    try:
        encoded = c.encode('gb2312')
    except UnicodeEncodeError as e:
        raise GB2312Exception(f"'{c}' not a gb2312 char") from e
    if len(encoded) == 1:
        raise GB2312Exception(f"'{c}' is a ascii char")
    row = encoded[0] - _euc_offset
    col = encoded[1] - _euc_offset
    return row, col


def chr_categories() -> list[str]:
    return ['other', 'level-1', 'level-2']


def query_category(c: str) -> str | None:
    try:
        row = query_coord(c)[0]
    except GB2312Exception:
        return None
    if 1 <= row <= 9:
        return 'other'
    elif 16 <= row <= 55:
        return 'level-1'
    elif 56 <= row <= 87:
        return 'level-2'
    else:
        raise AssertionError(f'Impossible row: {row}')


def _get_alphabet_by_rows_between(row_start, row_end) -> list[str]:
    alphabet = []
    for row in range(row_start, row_end + 1):
        for col in range(1, 94 + 1):
            try:
                alphabet.append(query_chr(row, col))
            except GB2312Exception:
                pass
    return alphabet


_alphabet_other = _get_alphabet_by_rows_between(1, 9)
_alphabet_level_1 = _get_alphabet_by_rows_between(16, 55)
_alphabet_level_2 = _get_alphabet_by_rows_between(56, 87)
_alphabet = _alphabet_other + _alphabet_level_1 + _alphabet_level_2


def get_alphabet_other() -> list[str]:
    return list(_alphabet_other)


def get_alphabet_level_1() -> list[str]:
    return list(_alphabet_level_1)


def get_alphabet_level_2() -> list[str]:
    return list(_alphabet_level_2)


def get_alphabet() -> list[str]:
    return list(_alphabet)


def other_count() -> int:
    return len(_alphabet_other)


def level_1_count() -> int:
    return len(_alphabet_level_1)


def level_2_count() -> int:
    return len(_alphabet_level_2)


def count() -> int:
    return len(_alphabet)
