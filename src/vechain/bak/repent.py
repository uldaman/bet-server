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
            "name": "combatant",
            "type": "uint256"
        },
        {
            "indexed": False,
            "name": "bets",
            "type": "uint256"
        }
    ],
    "name": "_repent",
    "type": "event",
    "signature": "0x73eed075d58172e0b579e14129d5943b894bbc02470e758208ed3cf164b4e7a9"
}


repent = EventDecoder(__abi)
