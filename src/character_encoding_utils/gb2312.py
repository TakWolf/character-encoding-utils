
_euc_offset = 0xA0


class GB2312Exception(Exception):
    pass


class GB2312EncodeError(GB2312Exception):
    def __init__(self, obj: str, position: int, reason: str):
        self.object = obj
        self.position = position
        self.reason = reason
        super().__init__(f"'gb2312' codec can't encode character '\\u{ord(obj):x}' in position {position}: {reason}")


class GB2312DecodeError(GB2312Exception):
    def __init__(self, obj: bytes, position: int, reason: str):
        self.object = obj
        self.position = position
        self.reason = reason
        super().__init__(f"'gb2312' codec can't decode byte 0x{obj[0]:x} in position {position}: {reason}")


def encode(cs: str) -> bytes:
    bs = bytearray()
    for position, c in enumerate(cs):
        try:
            bs.extend(c.encode('gb2312'))
        except UnicodeEncodeError as e:
            raise GB2312EncodeError(c, position, e.reason) from e
    return bytes(bs)


def decode(bs: bytes) -> str:
    cs = []
    bs = iter(bs)
    position = -1
    while True:
        try:
            b1 = next(bs)
            position += 1
        except StopIteration:
            break
        b2 = None
        if b1 > 0x7F:
            try:
                b2 = next(bs)
                position += 1
            except StopIteration:
                pass
        if b2 is None:
            bc = bytes([b1])
        else:
            bc = bytes([b1, b2])
        try:
            cs.append(bc.decode('gb2312'))
        except UnicodeDecodeError as e:
            raise GB2312DecodeError(bc, position, e.reason) from e
    return ''.join(cs)


def query_coord(c: str) -> tuple[int, int]:
    if len(c) != 1:
        raise GB2312Exception('must be one character')
    try:
        bs = encode(c)
    except GB2312EncodeError as e:
        raise GB2312Exception(f"'{c}' is not a 'gb2312' character") from e
    if len(bs) == 1:
        raise GB2312Exception(f"'{c}' is a ascii character")
    row = bs[0] - _euc_offset
    col = bs[1] - _euc_offset
    return row, col


def query_chr(row: int, col: int) -> str:
    if row < 1 or row > 94 or col < 1 or col > 94:
        raise GB2312Exception(f"'row' and 'col' must between 1 and 94")
    try:
        return decode(bytes([row + _euc_offset, col + _euc_offset]))
    except GB2312DecodeError as e:
        raise GB2312Exception(f"'gb2312' coord at ({row}, {col}) is undefined'") from e


def get_categories() -> list[str]:
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
        raise None


def _build_alphabet_by_rows_between(row_start: int, row_end: int) -> list[str]:
    alphabet = []
    for row in range(row_start, row_end + 1):
        for col in range(1, 94 + 1):
            try:
                c = query_chr(row, col)
                alphabet.append(c)
            except GB2312Exception:
                pass
    return alphabet


_alphabet_other = _build_alphabet_by_rows_between(1, 9)
_alphabet_level_1 = _build_alphabet_by_rows_between(16, 55)
_alphabet_level_2 = _build_alphabet_by_rows_between(56, 87)
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
