import json
from typing import Dict
from vechain import Contract


contarct = Contract('0x5B04bCEb87902E7D729fb9B2b561DF0338012c4e',
                    'https://sync-testnet.vechain.org')
start_block_num = 2294150
to_block_num = 400000000


def get_abi_from_file(file_path: str) -> Dict:
    with open('contract.json', 'r') as contract_file:
        contract_json = contract_file.read()
    contract = json.loads(contract_json)
    return contract['abi']


if __name__ == "__main__":
    from event_handler import handle_event
    abis = filter(lambda x: x.get('type', '') == 'event',
                  get_abi_from_file('contract.json'))

    events = {
        '_creat':  [],
        '_cancel':  [],
        '_lock':  [],
        '_finish':  [],
        '_join':  [],
        '_repent':  [],
    }

    for abi in abis:
        for event in contarct.get_events(start_block_num, to_block_num, abi):
            if event.name in events:
                events[event.name].append(event.args)

    for name, events in events.items():
        for event in events:
            handle_event(name, event)
