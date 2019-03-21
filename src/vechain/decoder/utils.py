from eth_utils import to_bytes, to_int, encode_hex as encode_hex_0x


TT256 = 2 ** 256


def zpad(x, l):
    """ Left zero pad value `x` at least to length `l`.

    >>> zpad('', 1)
    '\x00'
    >>> zpad('\xca\xfe', 4)
    '\x00\x00\xca\xfe'
    >>> zpad('\xff', 1)
    '\xff'
    >>> zpad('\xca\xfe', 2)
    '\xca\xfe'
    """
    return b'\x00' * max(0, l - len(x)) + x


def rzpad(value, total_length):
    """ Right zero pad value `x` at least to length `l`.

    >>> zpad('', 1)
    '\x00'
    >>> zpad('\xca\xfe', 4)
    '\xca\xfe\x00\x00'
    >>> zpad('\xff', 1)
    '\xff'
    >>> zpad('\xca\xfe', 2)
    '\xca\xfe'
    """
    return value + b'\x00' * max(0, total_length - len(value))


def is_numeric(x):
    return isinstance(x, int)


def is_string(x):
    return isinstance(x, bytes)


def ceil32(x):
    return x if x % 32 == 0 else x + 32 - (x % 32)


def hexstr_to_int(x):
    return to_int(hexstr=x)


def hexstr_to_bytes(x):
    return to_bytes(hexstr=x)


def normalize_name(name):
    ''' Return normalized event/function name. '''
    if '(' in name:
        return name[:name.find('(')]

    return name


def to_string(value):
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return bytes(value, 'utf-8')
    if isinstance(value, int):
        return bytes(str(value), 'utf-8')


def to_string_for_regexp(value):
    return str(to_string(value), 'utf-8')


def int_to_big_endian(value: int) -> bytes:
    return value.to_bytes((value.bit_length() + 7) // 8 or 1, "big")


def big_endian_to_int(value: bytes) -> int:
    return int.from_bytes(value, "big")


def encode_int(v):
    """encodes an integer into serialization"""
    if not is_numeric(v) or v < 0 or v >= TT256:
        raise Exception("Integer invalid or out of range: %r" % v)
    return int_to_big_endian(v)


def encode_hex(n):
    if isinstance(n, str):
        return encode_hex(n.encode('ascii'))
    return encode_hex_0x(n)[2:]
