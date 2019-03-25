import re
from utils import *
from collections import namedtuple


Event = namedtuple('Event', ['name', 'args', 'block'])


class EventDecoder(object):

    def __init__(self, abi):
        super(EventDecoder, self).__init__()

        self.event_data = {}

        if abi.get('type', None) != 'event':
            raise ValueError('The abi type is must be event')

        if 'signature' not in abi:
            raise ValueError('The abi must have signature field')

        normalized_name = normalize_name(abi['name'])
        indexed = [
            element['indexed']
            for element in abi['inputs']
        ]
        args = [
            element['name']
            for element in abi['inputs']
        ]
        encode_types = [
            element['type']
            for element in abi.get('inputs', [])
        ]
        self.event_data[abi['signature']] = {
            'types': encode_types,
            'name': normalized_name,
            'args': args,
            'indexed': indexed,
            'anonymous': abi.get('anonymous', False),
        }

    def decode_event(self, log):
        """ Return a dictionary representation the log.

        Note:
            This function won't work with anonymous events.

        Args:
            log_topics (List[hex_string]): The log's indexed arguments.
            log_data (hex_string): The encoded non-indexed arguments.
        """
        # https://github.com/ethereum/wiki/wiki/Ethereum-Contract-ABI#function-selector-and-argument-encoding

        # topics[0]: keccak(EVENT_NAME+"("+EVENT_ARGS.map(canonical_type_of).join(",")+")")
        # If the event is declared as anonymous the topics[0] is not generated;

        log_topics = log['topics']
        log_data = log['data']

        if not len(log_topics) or log_topics[0] not in self.event_data:
            raise ValueError('Unknown log type')

        event = self.event_data[log_topics[0]]
        log_topics = list(map(hexstr_to_int, log_topics[1:]))  # skip topics[0]
        log_data = hexstr_to_bytes(log_data)

        # data: abi_serialise(EVENT_NON_INDEXED_ARGS)
        # EVENT_NON_INDEXED_ARGS is the series of EVENT_ARGS that are not
        # indexed, abi_serialise is the ABI serialisation function used for
        # returning a series of typed values from a function.
        unindexed_types = [
            type_
            for type_, indexed in zip(event['types'], event['indexed'])
            if not indexed
        ]
        unindexed_args = _decode_abi(unindexed_types, log_data)

        # topics[n]: EVENT_INDEXED_ARGS[n - 1]
        # EVENT_INDEXED_ARGS is the series of EVENT_ARGS that are indexed
        indexed_count = 0

        result = {}
        for arg, type_, indexed in zip(
                event['args'], event['types'], event['indexed']):
            if indexed:
                log_topic = log_topics[indexed_count]
                indexed_count += 1

                if event['types'] == 'string':  # string indexed is a hash, so can't decode
                    value = '%#x' % log_topic
                else:
                    topic_bytes = zpad(
                        encode_int(log_topic),
                        32,
                    )
                    value = _decode_single(_process_type(type_), topic_bytes)
            else:
                value = unindexed_args.pop(0)
            result[arg] = value

        return Event(event['name'], result, log['meta']['blockNumber'])


# Decodes multiple arguments using the head/tail mechanism
def _decode_abi(types, data):
    # Process types
    proctypes = [_process_type(typ) for typ in types]
    # Get sizes of everything
    sizes = [_get_size(typ) for typ in proctypes]
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
    return [_dec(proctypes[i], outs[i]) for i in range(len(outs))]


# Decodes a single base datum
def _decode_single(typ, data):
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
        raise EncodingError("Unhandled type: %r %r" % (base, sub))


def _process_type(typ):
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
def _get_size(typ):
    base, sub, arrlist = typ
    if not len(arrlist):
        if base in ('string', 'bytes') and not sub:
            return None
        return 32
    if arrlist[-1] == []:
        return None
    o = _get_size((base, sub, arrlist[:-1]))
    if o is None:
        return None
    return arrlist[-1][0] * o


# Decode a single value (static or dynamic)
def _dec(typ, arg):
    base, sub, arrlist = typ
    sz = _get_size(typ)
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
        subsize = _get_size(subtyp)
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
            return [_dec(subtyp, out) for out in outs]
        # If children are static, then grab the data slice for each one and
        # sequentially decode them manually
        else:
            return [_dec(subtyp, arg[32 + subsize * i: 32 + subsize * (i + 1)])
                    for i in range(L)]
    # Static-sized arrays: decode piece-by-piece
    elif len(arrlist):
        L = arrlist[-1][0]
        subtyp = base, sub, arrlist[:-1]
        subsize = _get_size(subtyp)
        return [_dec(subtyp, arg[subsize * i:subsize * (i + 1)])
                for i in range(L)]
    else:
        return _decode_single(typ, arg)
