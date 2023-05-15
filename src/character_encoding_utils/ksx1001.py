
_euc_offset = 0xA0


class KSX1001Exception(Exception):
    pass


class KSX1001EncodeError(KSX1001Exception):
    def __init__(self, obj: str, position: int, reason: str):
        self.object = obj
        self.position = position
        self.reason = reason
        super().__init__(f"'ksx1001' codec can't encode character '\\u{ord(obj):x}' in position {position}: {reason}")


class KSX1001DecodeError(KSX1001Exception):
    def __init__(self, obj: bytes, position: int, reason: str):
        self.object = obj
        self.position = position
        self.reason = reason
        super().__init__(f"'ksx1001' codec can't decode byte 0x{obj[0]:x} in position {position}: {reason}")


def encode(cs: str) -> bytes:
    bs = bytearray()
    for i, c in enumerate(cs):
        try:
            bs.extend(c.encode('ksx1001'))
        except UnicodeEncodeError as e:
            raise KSX1001EncodeError(c, i, e.reason) from e
    return bytes(bs)


def decode(bs: bytes) -> str:
    cs = []
    for i in range(0, len(bs), 2):
        data = [bs[i]]
        if i + 1 < len(bs):
            data.append(bs[i + 1])
        bc = bytes(data)
        # 'euc_kr' 编码器对字符 'Hangul Filler (0x3164, row = 4, col= 52)' 的处理不正确，但是官方开发者并不认为这是一个错误
        # 问题详情见： https://github.com/python/cpython/issues/101863
        if bc == b'\xa4\xd4':
            cs.append(chr(0x3164))
        else:
            try:
                cs.append(bc.decode('ksx1001'))
            except UnicodeDecodeError as e:
                raise KSX1001DecodeError(bc, i, e.reason) from e
    return ''.join(cs)


def query_coord(c: str) -> tuple[int, int]:
    if len(c) != 1:
        raise KSX1001Exception('must be one character')
    try:
        bs = encode(c)
    except KSX1001EncodeError as e:
        raise KSX1001Exception(f"'{c}' is not a 'ksx1001' character") from e
    if len(bs) == 1:
        raise KSX1001Exception(f"'{c}' is a ascii character")
    row = bs[0] - _euc_offset
    col = bs[1] - _euc_offset
    return row, col


def query_chr(row: int, col: int):
    if row < 1 or row > 94 or col < 1 or col > 94:
        raise KSX1001Exception(f"'row' and 'col' must between 1 and 94")
    try:
        return decode(bytes([row + _euc_offset, col + _euc_offset]))
    except KSX1001DecodeError as e:
        raise KSX1001Exception(f"'ksx1001' coord at ({row}, {col}) is undefined'") from e


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
        raise None


def _build_alphabet_by_rows_between(row_start: int, row_end: int) -> list[str]:
    alphabet = []
    for row in range(row_start, row_end + 1):
        for col in range(1, 94 + 1):
            try:
                c = query_chr(row, col)
                alphabet.append(c)
            except KSX1001Exception:
                pass
    return alphabet


_alphabet_other = _build_alphabet_by_rows_between(1, 12)
_alphabet_syllable = _build_alphabet_by_rows_between(16, 40)
_alphabet_hanja = _build_alphabet_by_rows_between(42, 93)
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
