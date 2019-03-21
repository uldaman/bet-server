import numbers
import collections


bytes_types = (bytes, bytearray)
integer_types = (int,)
text_types = (str,)
string_types = (bytes, str, bytearray)


def is_integer(value) -> bool:
    return isinstance(value, integer_types) and not isinstance(value, bool)


def is_bytes(value) -> bool:
    return isinstance(value, bytes_types)


def is_text(value) -> bool:
    return isinstance(value, text_types)


def is_string(value) -> bool:
    return isinstance(value, string_types)


def is_boolean(value) -> bool:
    return isinstance(value, bool)


def is_dict(obj) -> bool:
    return isinstance(obj, collections.Mapping)


def is_list_like(obj) -> bool:
    return not is_string(obj) and isinstance(obj, collections.Sequence)


def is_list(obj) -> bool:
    return isinstance(obj, list)


def is_tuple(obj) -> bool:
    return isinstance(obj, tuple)


def is_null(obj) -> bool:
    return obj is None


def is_number(obj) -> bool:
    return isinstance(obj, numbers.Number)


def to_bytes(primitive=None, hexstr=None, text=None):
    if is_boolean(primitive):
        return b"\x01" if primitive else b"\x00"
    elif isinstance(primitive, bytearray):
        return bytes(primitive)
    elif isinstance(primitive, bytes):
        return primitive
    elif is_integer(primitive):
        return to_bytes(hexstr=to_hex(primitive))
    elif hexstr is not None:
        if len(hexstr) % 2:
            # type check ignored here because casting an Optional arg to str is not possible
            hexstr = "0x0" + remove_0x_prefix(hexstr)  # type: ignore
        return decode_hex(hexstr)
    elif text is not None:
        return text.encode("utf-8")
    raise TypeError(
        "expected a bool, int, byte or bytearray in first arg, or keyword of hexstr or text"
    )
