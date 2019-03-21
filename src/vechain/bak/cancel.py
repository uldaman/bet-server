from event import EventDecoder

__abi = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "name": "_id",
            "type": "uint256"
        }
    ],
    "name": "_cancel",
    "type": "event",
    "signature": "0x4efae47c6e6478ccc4dce1a2eefdbc93ba85a2822602ec18860a9ea5ce841c5b"
}


cancel = EventDecoder(__abi)
