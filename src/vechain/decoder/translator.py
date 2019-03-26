import re
from utils import *


# Decode a single value (static or dynamic)
def dec(typ, arg):
    base, sub, arrlist = typ
    sz = get_size(typ)
    # Dynamic-sized strings are encoded as <len(str)> + <str>
    if base in ('string', 'bytes') and not sub:
        L = big_endian_to_int(arg[:32])
        assert len(arg[32:]) == ceil32(
            L), "Wrong data size for string/bytes object: expected %d actual %d" % (ceil32(L), len(arg[32:]))
        return str(arg[32:][:L], 'utf-8')
    # Dynamic-sized arrays
    elif sz is None:
        L = big_endian_to_int(arg[:32])
        subtyp = base, sub, arrlist[:-1]
        subsize = get_size(subtyp)
        # If children are dynamic, use the head/tail mechanism. Fortunately,
        # here the code is simpler since we do not have to worry about
        # mixed dynamic and static children, as we do in the top-level multi-arg
        # case
        if subsize is None:
            assert len(arg) >= 32 + 32 * L, "Not enough data for head"
            start_positions = [big_endian_to_int(arg[32 + 32 * i: 64 + 32 * i])
                               for i in range(L)] + [len(arg)]
            outs = [arg[start_positions[i]: start_positions[i + 1]]
                    for i in range(L)]
            return [dec(subtyp, out) for out in outs]
        # If children are static, then grab the data slice for each one and
        # sequentially decode them manually
        else:
            return [dec(subtyp, arg[32 + subsize * i: 32 + subsize * (i + 1)])
                    for i in range(L)]
    # Static-sized arrays: decode piece-by-piece
    elif len(arrlist):
        L = arrlist[-1][0]
        subtyp = base, sub, arrlist[:-1]
        subsize = get_size(subtyp)
        return [dec(subtyp, arg[subsize * i:subsize * (i + 1)])
                for i in range(L)]
    else:
        return decode_single(typ, arg)


# Decodes multiple arguments using the head/tail mechanism
def decode_abi(types, data):
    # Process types
    proctypes = [process_type(typ) for typ in types]
    # Get sizes of everything
    sizes = [get_size(typ) for typ in proctypes]
    # Initialize array of outputs
    outs = [None] * len(types)
    # Initialize array of start positions
    start_positions = [None] * len(types) + [len(data)]
    # If a type is static, grab the data directly, otherwise record
    # its start position
    pos = 0
    for i, typ in enumerate(types):
        if sizes[i] is None:
            start_positions[i] = big_endian_to_int(data[pos:pos + 32])
            j = i - 1
            while j >= 0 and start_positions[j] is None:
                start_positions[j] = start_positions[i]
                j -= 1
            pos += 32
        else:
            outs[i] = data[pos:pos + sizes[i]]
            pos += sizes[i]
    # We add a start position equal to the length of the entire data
    # for convenience.
    j = len(types) - 1
    while j >= 0 and start_positions[j] is None:
        start_positions[j] = start_positions[len(types)]
        j -= 1
    assert pos <= len(data), "Not enough data for head"
    # Grab the data for tail arguments using the start positions
    # calculated above
    for i, typ in enumerate(types):
        if sizes[i] is None:
            offset = start_positions[i]
            next_offset = start_positions[i + 1]
            outs[i] = data[offset:next_offset]
    # Recursively decode them all
    return [dec(proctypes[i], outs[i]) for i in range(len(outs))]


# Decodes a single base datum
def decode_single(typ, data):
    base, sub, _ = typ
    if base == 'address':
        return '0x' + encode_hex(data[12:])
    elif base == 'hash':
        return data[32 - int(sub):]
    elif base == 'string' or base == 'bytes':
        if len(sub):
            return data[:int(sub)]
        else:
            l = big_endian_to_int(data[0:32])
            return data[32:][:l]
    elif base == 'uint':
        return big_endian_to_int(data) % 2**int(sub)
    elif base == 'int':
        o = big_endian_to_int(data) % 2 ** int(sub)
        return (o - 2 ** int(sub)) if o >= 2 ** (int(sub) - 1) else o
    elif base == 'ufixed':
        high, low = [int(x) for x in sub.split('x')]
        return big_endian_to_int(data) * 1.0 // 2 ** low
    elif base == 'fixed':
        high, low = [int(x) for x in sub.split('x')]
        o = big_endian_to_int(data)
        i = (o - 2 ** (high + low)) if o >= 2 ** (high + low - 1) else o
        return (i * 1.0 // 2 ** low)
    elif base == 'decimal':
        o = big_endian_to_int(data)
        i = (o - 2 ** 256 if o > 2 ** 255 else o)
        return i / 10 ** int(sub)
    elif base == 'bool':
        return bool(int(encode_hex(data), 16))
    else:
        raise Exception("Unhandled type: %r %r" % (base, sub))


def process_type(typ):
    # Crazy reg expression to separate out base type component (eg. uint),
    # size (eg. 256, 128x128, none), array component (eg. [], [45], none)
    regexp = '([a-z]*)([0-9]*x?[0-9]*)((\[[0-9]*\])*)'
    base, sub, arr, _ = re.match(
        regexp, to_string_for_regexp(typ)).groups()
    arrlist = re.findall('\[[0-9]*\]', arr)
    assert len(''.join(arrlist)) == len(arr), \
        "Unknown characters found in array declaration"
    # Check validity of string type
    if base == 'string' or base == 'bytes':
        assert re.match('^[0-9]*$', sub), \
            "String type must have no suffix or numerical suffix"
        assert not sub or int(sub) <= 32, \
            "Maximum 32 bytes for fixed-length str or bytes"
    # Check validity of integer type
    elif base == 'uint' or base == 'int':
        assert re.match('^[0-9]+$', sub), \
            "Integer type must have numerical suffix"
        assert 8 <= int(sub) <= 256, \
            "Integer size out of bounds"
        assert int(sub) % 8 == 0, \
            "Integer size must be multiple of 8"
    # Check validity of fixed type
    elif base == 'ufixed' or base == 'fixed':
        assert re.match('^[0-9]+x[0-9]+$', sub), \
            "Real type must have suffix of form <high>x<low>, eg. 128x128"
        high, low = [int(x) for x in sub.split('x')]
        assert 8 <= (high + low) <= 256, \
            "Real size out of bounds (max 32 bytes)"
        assert high % 8 == 0 and low % 8 == 0, \
            "Real high/low sizes must be multiples of 8"
    # Check validity of hash type
    elif base == 'hash':
        assert re.match('^[0-9]+$', sub), \
            "Hash type must have numerical suffix"
    # Check validity of address type
    elif base == 'address':
        assert sub == '', "Address cannot have suffix"
    return base, sub, [ast.literal_eval(x) for x in arrlist]


# Returns the static size of a type, or None if dynamic
def get_size(typ):
    base, sub, arrlist = typ
    if not len(arrlist):
        if base in ('string', 'bytes') and not sub:
            return None
        return 32
    if arrlist[-1] == []:
        return None
    o = get_size((base, sub, arrlist[:-1]))
    if o is None:
        return None
    return arrlist[-1][0] * o


# Encodes a single value (static or dynamic)
def enc(typ, arg):
    base, sub, arrlist = typ
    type_size = get_size(typ)

    if base in ('string', 'bytes') and not sub:
        return encode_single(typ, arg)

    # Encode dynamic-sized lists via the head/tail mechanism described in
    # https://github.com/ethereum/wiki/wiki/Proposal-for-new-ABI-value-encoding
    if type_size is None:
        assert isinstance(arg, list), \
            "Expecting a list argument"
        subtyp = base, sub, arrlist[:-1]
        subsize = get_size(subtyp)
        myhead, mytail = b'', b''
        if arrlist[-1] == []:
            myhead += enc(INT256, len(arg))
        else:
            assert len(arg) == arrlist[-1][0], \
                "Wrong array size: found %d, expecting %d" % \
                (len(arg), arrlist[-1][0])
        for i in range(len(arg)):
            if subsize is None:
                myhead += enc(INT256, 32 * len(arg) + len(mytail))
                mytail += enc(subtyp, arg[i])
            else:
                myhead += enc(subtyp, arg[i])
        return myhead + mytail
    # Encode static-sized lists via sequential packing
    else:
        if arrlist == []:
            return to_string(encode_single(typ, arg))
        else:
            subtyp = base, sub, arrlist[:-1]
            o = b''
            assert len(arg) == arrlist[-1][0], "Incorrect array size"
            for x in arg:
                o += enc(subtyp, x)
            return o


# Encodes multiple arguments using the head/tail mechanism
def encode_abi(types, args):
    headsize = 0
    proctypes = [process_type(typ) for typ in types]
    sizes = [get_size(typ) for typ in proctypes]
    for i, arg in enumerate(args):
        if sizes[i] is None:
            headsize += 32
        else:
            headsize += sizes[i]
    myhead, mytail = b'', b''
    for i, arg in enumerate(args):
        if sizes[i] is None:
            myhead += enc(INT256, headsize + len(mytail))
            mytail += enc(proctypes[i], args[i])
        else:
            myhead += enc(proctypes[i], args[i])
    return myhead + mytail


def encode_single(typ, arg):  # pylint: disable=too-many-return-statements,too-many-branches,too-many-statements,too-many-locals
    """ Encode `arg` as `typ`.

    `arg` will be encoded in a best effort manner, were necessary the function
    will try to correctly define the underlying binary representation (ie.
    decoding a hex-encoded address/hash).

    Args:
        typ (Tuple[(str, int, list)]): A 3-tuple defining the `arg` type.

            The first element defines the type name.
            The second element defines the type length in bits.
            The third element defines if it's an array type.

            Together the first and second defines the elementary type, the third
            element must be present but is ignored.

            Valid type names are:
                - uint
                - int
                - bool
                - ufixed
                - fixed
                - string
                - bytes
                - hash
                - address

        arg (object): The object to be encoded, it must be a python object
            compatible with the `typ`.

    Raises:
        ValueError: when an invalid `typ` is supplied.
        Exception: when `arg` cannot be encoded as `typ` because of the
            binary contraints.

    Note:
        This function don't work with array types, for that use the `enc`
        function.
    """
    base, sub, _ = typ

    if base == 'uint':
        sub = int(sub)

        if not (0 < sub <= 256 and sub % 8 == 0):
            raise ValueError(
                'invalid unsigned integer bit length {}'.format(sub))

        try:
            i = decint(arg, signed=False)
        except Exception:
            # arg is larger than 2**256
            raise Exception(repr(arg))

        if not 0 <= i < 2 ** sub:
            raise Exception(repr(arg))

        value_encoded = int_to_big_endian(i)
        return zpad(value_encoded, 32)

    if base == 'int':
        sub = int(sub)
        bits = sub - 1

        if not (0 < sub <= 256 and sub % 8 == 0):
            raise ValueError('invalid integer bit length {}'.format(sub))

        try:
            i = decint(arg, signed=True)
        except Exception:
            # arg is larger than 2**255
            raise Exception(repr(arg))

        if not -2 ** bits <= i < 2 ** bits:
            raise Exception(repr(arg))

        value = i % 2 ** 256  # convert negative to "equivalent" positive
        value_encoded = int_to_big_endian(value)
        return zpad(value_encoded, 32)

    if base == 'bool':
        if arg is True:
            value_encoded = int_to_big_endian(1)
        elif arg is False:
            value_encoded = int_to_big_endian(0)
        else:
            raise ValueError('%r is not bool' % arg)

        return zpad(value_encoded, 32)

    if base == 'ufixed':
        sub = str(sub)  # pylint: disable=redefined-variable-type

        high_str, low_str = sub.split('x')
        high = int(high_str)
        low = int(low_str)

        if not (0 < high + low <= 256 and high % 8 == 0 and low % 8 == 0):
            raise ValueError('invalid unsigned fixed length {}'.format(sub))

        if not 0 <= arg < 2 ** high:
            raise Exception(repr(arg))

        float_point = arg * 2 ** low
        fixed_point = int(float_point)
        return zpad(int_to_big_endian(fixed_point), 32)

    if base == 'fixed':
        sub = str(sub)  # pylint: disable=redefined-variable-type

        high_str, low_str = sub.split('x')
        high = int(high_str)
        low = int(low_str)
        bits = high - 1

        if not (0 < high + low <= 256 and high % 8 == 0 and low % 8 == 0):
            raise ValueError('invalid unsigned fixed length {}'.format(sub))

        if not -2 ** bits <= arg < 2 ** bits:
            raise Exception(repr(arg))

        float_point = arg * 2 ** low
        fixed_point = int(float_point)
        value = fixed_point % 2 ** 256
        return zpad(int_to_big_endian(value), 32)

    # Decimals
    if base == 'decimal':
        val_to_encode = int(arg * 10**int(sub))
        return zpad(encode_int(val_to_encode % 2**256), 32)

    if base == 'string':
        if isinstance(arg, unicode):
            arg = arg.encode('utf8')
        else:
            try:
                arg.decode('utf8')
            except UnicodeDecodeError:
                raise ValueError('string must be utf8 encoded')

        if len(sub):  # fixed length
            if not 0 <= len(arg) <= int(sub):
                raise ValueError('invalid string length {}'.format(sub))

            if not 0 <= int(sub) <= 32:
                raise ValueError('invalid string length {}'.format(sub))

            return rzpad(arg, 32)

        if not 0 <= len(arg) < TT256:
            raise Exception('Integer invalid or out of range: %r' % arg)

        length_encoded = zpad(int_to_big_endian(len(arg)), 32)
        value_encoded = rzpad(arg, ceil32(len(arg)))

        return length_encoded + value_encoded

    if base == 'bytes':
        if not is_string(arg):
            if isinstance(arg, str):
                arg = bytes(arg, 'utf8')
            else:
                raise Exception('Expecting string: %r' % arg)

        arg = to_string(arg)  # py2: force unicode into str

        if len(sub):  # fixed length
            if not 0 <= len(arg) <= int(sub):
                raise ValueError('string must be utf8 encoded')

            if not 0 <= int(sub) <= 32:
                raise ValueError('string must be utf8 encoded')

            return rzpad(arg, 32)

        if not 0 <= len(arg) < TT256:
            raise Exception('Integer invalid or out of range: %r' % arg)

        length_encoded = zpad(int_to_big_endian(len(arg)), 32)
        value_encoded = rzpad(arg, ceil32(len(arg)))

        return length_encoded + value_encoded

    if base == 'hash':
        if not (int(sub) and int(sub) <= 32):
            raise Exception('too long: %r' % arg)

        if is_numeric(arg):
            return zpad(encode_int(arg), 32)

        if len(arg) == int(sub):
            return zpad(arg, 32)

        if len(arg) == int(sub) * 2:
            return zpad(decode_hex(arg), 32)

        raise Exception('Could not parse hash: %r' % arg)

    if base == 'address':
        assert sub == ''

        if is_numeric(arg):
            return zpad(encode_int(arg), 32)

        if len(arg) == 20:
            return zpad(arg, 32)

        if len(arg) == 40:
            return zpad(decode_hex(arg), 32)

        if len(arg) == 42 and arg[:2] == '0x':
            return zpad(decode_hex(arg[2:]), 32)

        raise Exception('Could not parse address: %r' % arg)
    raise Exception('Unhandled type: %r %r' % (base, sub))


def decint(n, signed=False):  # pylint: disable=invalid-name,too-many-branches
    """ Decode an unsigned/signed integer. """

    if isinstance(n, str):
        n = to_string(n)

    if n is True:
        return 1

    if n is False:
        return 0

    if n is None:
        return 0

    if is_numeric(n):
        if signed:
            if not -TT255 <= n <= TT255 - 1:
                raise Exception('Number out of range: %r' % n)
        else:
            if not 0 <= n <= TT256 - 1:
                raise Exception('Number out of range: %r' % n)

        return n

    if is_string(n):
        if len(n) > 32:
            raise Exception('String too long: %r' % n)

        if len(n) == 40:
            int_bigendian = decode_hex(n)
        else:
            int_bigendian = n  # pylint: disable=redefined-variable-type

        result = big_endian_to_int(int_bigendian)
        if signed:
            if result >= TT255:
                result -= TT256

            if not -TT255 <= result <= TT255 - 1:
                raise Exception('Number out of range: %r' % n)
        else:
            if not 0 <= result <= TT256 - 1:
                raise Exception('Number out of range: %r' % n)

        return result

    raise Exception('Cannot decode integer: %r' % n)
