
class Big5Exception(Exception):
    pass


class Big5EncodeError(Big5Exception):
    def __init__(self, obj: str, position: int, reason: str):
        self.object = obj
        self.position = position
        self.reason = reason
        super().__init__(f"'big5' codec can't encode character '\\u{ord(obj):x}' in position {position}: {reason}")


class Big5DecodeError(Big5Exception):
    def __init__(self, obj: bytes, position: int, reason: str):
        self.object = obj
        self.position = position
        self.reason = reason
        super().__init__(f"'big5' codec can't decode byte 0x{obj[0]:x} in position {position}: {reason}")


def encode(cs: str) -> bytes:
    bs = bytearray()
    for i, c in enumerate(cs):
        # 此处默认编码器映射错误
        if c == '〸':
            bs.extend(b'\xa2\xcc')
        elif c == '〺':
            bs.extend(b'\xa2\xce')
        else:
            try:
                bs.extend(c.encode('big5'))
            except UnicodeEncodeError as e:
                raise Big5EncodeError(c, i, e.reason) from e
    return bytes(bs)


def decode(bs: bytes) -> str:
    cs = []
    for i in range(0, len(bs), 2):
        data = [bs[i]]
        if i + 1 < len(bs):
            data.append(bs[i + 1])
        bc = bytes(data)
        # 此处默认编码器映射错误
        if bc == b'\xa2\xcc':
            cs.append('〸')
        elif bs == b'\xa2\xce':
            cs.append('〺')
        else:
            try:
                cs.append(bc.decode('big5'))
            except UnicodeDecodeError as e:
                raise Big5DecodeError(bc, i, e.reason) from e
    return ''.join(cs)


def query_code(c: str) -> int:
    if len(c) != 1:
        raise Big5Exception('must be one character')
    try:
        bs = encode(c)
    except Big5EncodeError as e:
        raise Big5Exception(f"'{c}' is not a 'big5' character") from e
    if len(bs) == 1:
        raise Big5Exception(f"'{c}' is a ascii character")
    code = int(f'{bs[0]:02x}{bs[1]:02x}', 16)
    return code


def query_chr(code: int) -> str:
    try:
        return decode(bytes.fromhex(f'{code:X}'))
    except Big5DecodeError as e:
        raise Big5Exception(f"'big5' code 0x{code:04X} is undefined") from e


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


def _build_alphabet_by_codes_between(code_start: int, code_end: int) -> list[str]:
    alphabet = []
    for code in range(code_start, code_end + 1):
        try:
            c = query_chr(code)
            alphabet.append(c)
        except Big5Exception:
            pass
    return alphabet


_alphabet_other = _build_alphabet_by_codes_between(0xA140, 0xA3BF)
_alphabet_level_1 = _build_alphabet_by_codes_between(0xA440, 0xC67E)
_alphabet_level_2 = _build_alphabet_by_codes_between(0xC940, 0xF9D5)
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
