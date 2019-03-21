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
            "name": "gameName",
            "type": "string"
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
    "signature": "0xe4c99b8265cc805595cada13fd7992c47f2342d60278ccc81a5b03dec51fc391"
}

create = EventDecoder(__abi)
