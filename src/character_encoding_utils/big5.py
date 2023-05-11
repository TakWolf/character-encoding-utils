
class Big5Exception(Exception):
    pass


def query_chr(code: int) -> str:
    if code == 0xA2CC:
        return '〸'
    if code == 0xA2CE:
        return '〺'

    try:
        return bytes.fromhex(f'{code:X}').decode('big5')
    except UnicodeDecodeError as e:
        raise Big5Exception(f"big5 can't decode code '{code:X}'") from e


def query_code(c: str) -> int:
    if c == '〸':
        return 0xA2CC
    if c == '〺':
        return 0xA2CE

    if len(c) != 1:
        raise Big5Exception('Must be one char')
    try:
        encoded = c.encode('big5')
    except UnicodeEncodeError as e:
        raise Big5Exception(f"'{c}' not a big5 char") from e
    if len(encoded) == 1:
        raise Big5Exception(f"'{c}' is a ascii char")
    code = int(f'{encoded[0]:02x}{encoded[1]:02x}', 16)
    return code


def get_categories() -> list[str]:
    return ['other', 'level-1', 'level-2']


def query_category(c: str) -> str | None:
    try:
        code = query_code(c)
    except Big5Exception:
        return None
    if 0xA140 <= code <= 0xA3BF:
        return 'other'
    elif 0xA440 <= code <= 0xC67E:
        return 'level-1'
    elif 0xC940 <= code <= 0xF9D5:
        return 'level-2'
    else:
        return None


def _get_alphabet_by_codes_between(code_start, code_end) -> list[str]:
    alphabet = []
    for code in range(code_start, code_end + 1):
        try:
            c = query_chr(code)
            alphabet.append(c)
        except Big5Exception:
            pass
    return alphabet


_alphabet_other = _get_alphabet_by_codes_between(0xA140, 0xA3BF)
_alphabet_level_1 = _get_alphabet_by_codes_between(0xA440, 0xC67E)
_alphabet_level_2 = _get_alphabet_by_codes_between(0xC940, 0xF9D5)
_alphabet = _alphabet_other + _alphabet_level_1 + _alphabet_level_2


def get_alphabet_other() -> list[str]:
    return list(_alphabet_other)


def get_alphabet_level_1() -> list[str]:
    return list(_alphabet_level_1)


def get_alphabet_level_2() -> list[str]:
    return list(_alphabet_level_2)


def get_alphabet() -> list[str]:
    return list(_alphabet)


def get_other_count() -> int:
    return len(_alphabet_other)


def get_level_1_count() -> int:
    return len(_alphabet_level_1)


def get_level_2_count() -> int:
    return len(_alphabet_level_2)


def get_count() -> int:
    return len(_alphabet)
