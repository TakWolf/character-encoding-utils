import itertools


class ShiftJISException(Exception):
    pass


class ShiftJISEncodeError(ShiftJISException):
    def __init__(self, obj: str, position: int, reason: str):
        self.object = obj
        self.position = position
        self.reason = reason
        super().__init__(f"'shift-jis' codec can't encode character '\\u{ord(obj):x}' in position {position}: {reason}")


class ShiftJISDecodeError(ShiftJISException):
    def __init__(self, obj: bytes, position: int, reason: str):
        self.object = obj
        self.position = position
        self.reason = reason
        super().__init__(f"'shift-jis' codec can't decode byte 0x{obj[0]:x} in position {position}: {reason}")


def encode(cs: str) -> bytes:
    bs = bytearray()
    for i, c in enumerate(cs):
        try:
            bs.extend(c.encode('shift-jis'))
        except UnicodeEncodeError as e:
            raise ShiftJISEncodeError(c, i, e.reason) from e
    return bytes(bs)


def decode(bs: bytes) -> str:
    cs = []
    for i in range(0, len(bs), 2):
        data = [bs[i]]
        if i + 1 < len(bs):
            data.append(bs[i + 1])
        bc = bytes(data)
        try:
            cs.append(bc.decode('shift-jis'))
        except UnicodeDecodeError as e:
            raise ShiftJISDecodeError(bc, i, e.reason) from e
    return ''.join(cs)


def get_categories() -> list[str]:
    return ['single-ascii', 'single-other', 'double-other', 'double-kanji']


def query_category(c: str) -> str | None:
    try:
        bs = encode(c)
    except ShiftJISEncodeError:
        return None
    first_byte = bs[0]
    if len(bs) == 1:
        if 0x20 <= first_byte <= 0x7E:
            return 'single-ascii'
        elif 0xA1 <= first_byte <= 0xDF:
            return 'single-other'
        else:
            raise None
    else:
        second_byte = bs[1]
        if 0x81 <= first_byte <= 0x87 or (first_byte == 0x88 and second_byte <= 0x9E):
            return 'double-other'
        elif (first_byte == 0x88 and second_byte >= 0x9F) or 0x89 <= first_byte <= 0x9F or 0xE0 <= first_byte <= 0xEF:
            return 'double-kanji'
        else:
            raise None


def _build_alphabet_single_byte(byte_start: int, byte_end: int) -> list[str]:
    alphabet = []
    for code in range(byte_start, byte_end + 1):
        try:
            c = decode(bytes([code]))
            alphabet.append(c)
        except ShiftJISDecodeError:
            pass
    return alphabet


def _build_alphabet_double_other() -> list[str]:
    """
    第一位字节使用 0x81 ~ 0x87，第二位字节使用 0x40 ~ 0x7E、0x80 ~ 0xFC
    第一位字节使用 0x88，第二位字节使用 0x40 ~ 0x7E、0x80 ~ 0x9E
    """
    alphabet = []
    for first_byte in range(0x81, 0x88 + 1):
        for second_byte in range(0x40, 0x7E + 1):
            try:
                c = decode(bytes([first_byte, second_byte]))
                alphabet.append(c)
            except ShiftJISDecodeError:
                pass
        for second_byte in range(0x80, (0x9E if first_byte == 0x88 else 0xFC) + 1):
            try:
                c = decode(bytes([first_byte, second_byte]))
                alphabet.append(c)
            except ShiftJISDecodeError:
                pass
    return alphabet


def _build_alphabet_double_kanji() -> list[str]:
    """
    第一位字节使用 0x88，第二位字节使用 0x9F ~ 0xFC
    第一位字节使用 0x89 ~ 0x9F、0xE0 ~ 0xEF，第二位字节使用 0x40 ~ 0x7E、0x80 ~ 0xFC
    """
    alphabet = []
    for first_byte in itertools.chain(range(0x88, 0x9F + 1), range(0xE0, 0xEF + 1)):
        if first_byte >= 0x89:
            for second_byte in range(0x40, 0x7E + 1):
                try:
                    c = decode(bytes([first_byte, second_byte]))
                    alphabet.append(c)
                except ShiftJISDecodeError:
                    pass
        for second_byte in range(0x9F if first_byte == 0x88 else 0x80, 0xFC + 1):
            try:
                c = decode(bytes([first_byte, second_byte]))
                alphabet.append(c)
            except ShiftJISDecodeError:
                pass
    return alphabet


_alphabet_single_ascii = _build_alphabet_single_byte(0x20, 0x7E)
_alphabet_single_other = _build_alphabet_single_byte(0xA1, 0xDF)
_alphabet_double_other = _build_alphabet_double_other()
_alphabet_double_kanji = _build_alphabet_double_kanji()
_alphabet = _alphabet_single_ascii + _alphabet_single_other + _alphabet_double_other + _alphabet_double_kanji


def get_alphabet_single_ascii() -> list[str]:
    return list(_alphabet_single_ascii)


def get_alphabet_single_other() -> list[str]:
    return list(_alphabet_single_other)


def get_alphabet_double_other() -> list[str]:
    return list(_alphabet_double_other)


def get_alphabet_double_kanji() -> list[str]:
    return list(_alphabet_double_kanji)


def get_alphabet() -> list[str]:
    return list(_alphabet)


def get_single_ascii_count() -> int:
    return len(_alphabet_single_ascii)


def get_single_other_count() -> int:
    return len(_alphabet_single_other)


def get_double_other_count() -> int:
    return len(_alphabet_double_other)


def get_double_kanji_count() -> int:
    return len(_alphabet_double_kanji)


def get_count() -> int:
    return len(_alphabet)
