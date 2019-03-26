from translator import *
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
        unindexed_args = decode_abi(unindexed_types, log_data)

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
                    value = decode_single(process_type(type_), topic_bytes)
            else:
                value = unindexed_args.pop(0)
            result[arg] = value

        return Event(event['name'], result, log['meta']['blockNumber'])


if __name__ == "__main__":
    abi = {
        "anonymous": False,
        "inputs": [
          {
              "indexed": True,
              "name": "_id",
              "type": "uint256"
          },
            {
              "indexed": False,
              "name": "gameName",
              "type": "string"
          },
            {
              "indexed": False,
              "name": "startTime",
              "type": "uint256"
          },
            {
              "indexed": False,
              "name": "leftName",
              "type": "string"
          },
            {
              "indexed": False,
              "name": "rightName",
              "type": "string"
          }
        ],
        "name": "_creat",
        "type": "event",
        "signature": "0xb8c8322ac4e6ae368af6cfc837a0906e4ee9a35f49ef8b747adcd46dfdac5859"
    }
    log = {
        "address": "0x72ca1aafe8e8f84abbfba3705c35f084ecd21989",
        "topics": [
            "0xb8c8322ac4e6ae368af6cfc837a0906e4ee9a35f49ef8b747adcd46dfdac5859",
            "0x0000000000000000000000000000000000000000000000000000000000000001"
        ],
        "data": "0x000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000169a4b2da3900000000000000000000000000000000000000000000000000000000000000c00000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000001b32303139204c504c20e698a5e5ada3e8b59be5b8b8e8a784e8b59b00000000000000000000000000000000000000000000000000000000000000000000000003524e47000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000024947000000000000000000000000000000000000000000000000000000000000",
        "meta": {
            "blockID": "0x00236bbffd352f4a30b3b8e8d1773e85c8987d6e09aabd9c4acd3bca83025868",
            "blockNumber": 2321343,
            "blockTimestamp": 1553236420,
            "txID": "0x23af44abc5913797e560957485aef9daf39c20ae99eb84752812885a70fb9f38",
            "txOrigin": "0x6ca591b6cef74f2cb9cba3f8dfb50da45b021137"
        }
    }

    r = EventDecoder(abi).decode_event(log)
    print(r)
