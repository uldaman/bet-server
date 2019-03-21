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
    "name": "_lock",
    "type": "event",
    "signature": "0x8ec22837bcbc063bf52cff498b2e9675cec54e6a3b14d076c920a6c8272f99d0"
}


lock = EventDecoder(__abi)
