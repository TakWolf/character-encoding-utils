import itertools


class ShiftJISException(Exception):
    pass


class ShiftJISEncodeError(ShiftJISException):
    def __init__(self, obj: str, position: int, reason: str):
        super().__init__(f"'shift-jis' codec can't encode character '\\u{ord(obj):x}' in position {position}: {reason}")
        self.object = obj
        self.position = position
        self.reason = reason


class ShiftJISDecodeError(ShiftJISException):
    def __init__(self, obj: bytes, position: int, reason: str):
        if len(obj) <= 1:
            super().__init__(f"'shift-jis' codec can't decode byte 0x{obj[0]:x} in position {position}: {reason}")
        else:
            super().__init__(f"'shift-jis' codec can't decode bytes in position {position}-{position + len(obj) - 1}: {reason}")
        self.object = obj
        self.position = position
        self.reason = reason


def encode(cs: str) -> bytes:
    bs = bytearray()
    for position, c in enumerate(cs):
        if c == '\\':
            raise ShiftJISEncodeError(c, position, f"in 'shift-jis' the character '\\' is replaced with '¥'")
        elif c == '~':
            raise ShiftJISEncodeError(c, position, f"in 'shift-jis' the character '~' is replaced with '‾'")
        else:
            try:
                bs.extend(c.encode('shift-jis'))
            except UnicodeEncodeError as e:
                raise ShiftJISEncodeError(c, position, e.reason) from e
    return bytes(bs)


def decode(bs: bytes | bytearray) -> str:
    cs = []
    cursor = 0
    passed = 0
    while True:
        if cursor >= len(bs):
            break
        bc = bytearray([bs[cursor]])
        cursor += 1

        if not (bc[0] <= 0x7F or 0xA1 <= bc[0] <= 0xDF):
            if cursor < len(bs):
                bc.append(bs[cursor])
                cursor += 1

        if bc == b'\\':
            cs.append('¥')
        elif bc == b'~':
            cs.append('‾')
        else:
            try:
                cs.append(bc.decode('shift-jis'))
            except UnicodeDecodeError as e:
                raise ShiftJISDecodeError(bc, passed, e.reason) from e
        passed += len(bc)
    return ''.join(cs)


def get_categories() -> list[str]:
    return [
        'single-byte-ascii-control',
        'single-byte-ascii-printable',
        'single-byte-half-width-katakana',
        'double-byte-other',
        'double-byte-kanji',
    ]


def query_category(c: str) -> str | None:
    try:
        bs = encode(c)
    except ShiftJISEncodeError:
        return None
    first_byte = bs[0]
    if len(bs) == 1:
        if 0x00 <= first_byte <= 0x1F or first_byte == 0x7F:
            return 'single-byte-ascii-control'
        elif 0x20 <= first_byte <= 0x7E:
            return 'single-byte-ascii-printable'
        elif 0xA1 <= first_byte <= 0xDF:
            return 'single-byte-half-width-katakana'
        else:
            return None
    else:
        second_byte = bs[1]
        if 0x81 <= first_byte <= 0x87 or (first_byte == 0x88 and second_byte <= 0x9E):
            return 'double-byte-other'
        elif (first_byte == 0x88 and second_byte >= 0x9F) or 0x89 <= first_byte <= 0x9F or 0xE0 <= first_byte <= 0xEF:
            return 'double-byte-kanji'
        else:
            return None


def _build_alphabet_single_byte(byte_start: int, byte_end: int) -> list[str]:
    alphabet = []
    for code in range(byte_start, byte_end + 1):
        try:
            c = decode(bytes([code]))
            alphabet.append(c)
        except ShiftJISDecodeError:
            pass
    return alphabet


def _build_alphabet_double_byte_other() -> list[str]:
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


def _build_alphabet_double_byte_kanji() -> list[str]:
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


_alphabet_single_byte_ascii_control = _build_alphabet_single_byte(0x00, 0x1F)
_alphabet_single_byte_ascii_control.append(chr(0x7F))
_alphabet_single_byte_ascii_printable = _build_alphabet_single_byte(0x20, 0x7E)
_alphabet_single_byte_half_width_katakana = _build_alphabet_single_byte(0xA1, 0xDF)
_alphabet_double_byte_other = _build_alphabet_double_byte_other()
_alphabet_double_byte_kanji = _build_alphabet_double_byte_kanji()
_alphabet = _alphabet_single_byte_ascii_control + _alphabet_single_byte_ascii_printable + _alphabet_single_byte_half_width_katakana + _alphabet_double_byte_other + _alphabet_double_byte_kanji


def get_alphabet_single_byte_ascii_control() -> list[str]:
    return list(_alphabet_single_byte_ascii_control)


def get_alphabet_single_byte_ascii_printable() -> list[str]:
    return list(_alphabet_single_byte_ascii_printable)


def get_alphabet_single_byte_half_width_katakana() -> list[str]:
    return list(_alphabet_single_byte_half_width_katakana)


def get_alphabet_double_byte_other() -> list[str]:
    return list(_alphabet_double_byte_other)


def get_alphabet_double_byte_kanji() -> list[str]:
    return list(_alphabet_double_byte_kanji)


def get_alphabet() -> list[str]:
    return list(_alphabet)


def get_single_byte_ascii_control_count() -> int:
    return len(_alphabet_single_byte_ascii_control)


def get_single_byte_ascii_printable_count() -> int:
    return len(_alphabet_single_byte_ascii_printable)


def get_single_byte_half_width_katakana_count() -> int:
    return len(_alphabet_single_byte_half_width_katakana)


def get_double_byte_other_count() -> int:
    return len(_alphabet_double_byte_other)


def get_double_byte_kanji_count() -> int:
    return len(_alphabet_double_byte_kanji)


def get_count() -> int:
    return len(_alphabet)
