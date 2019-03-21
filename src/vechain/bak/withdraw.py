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
            "indexed": True,
            "name": "player",
            "type": "address"
        },
        {
            "indexed": False,
            "name": "award",
            "type": "uint256"
        }
    ],
    "name": "_withdraw",
    "type": "event",
    "signature": "0x491234459cc5c2ddc7327952ccf826b06930abbe200441971916f5e393da8872"
}

withdraw = EventDecoder(__abi)
