from event import EventDecoder

__abi = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "name": "_id",
            "type": "uint256"
        },
        {
            "indexed": False,
            "name": "winner",
            "type": "uint256"
        }
    ],
    "name": "_finish",
    "type": "event",
    "signature": "0x0927c65aa785cfbe2fdc3436508df236f9d1ba0b35b6ed3a55e73a3159dca7a8"
}

finish = EventDecoder(__abi)
