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
    "name": "_join",
    "type": "event",
    "signature": "0xadd33c52831a0b1c1f1f17c56aa20b5c040473e944e6f3475d38556c779df755"
}


join = EventDecoder(__abi)
