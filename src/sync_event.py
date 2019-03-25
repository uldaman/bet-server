import json
from event_handler import handle_event
from vechain import Contract, Block
from task import Task, Task_Queue


def get_abi_from_file(file_path: str):
    with open('contract.json', 'r') as contract_file:
        contract_json = contract_file.read()
    contract = json.loads(contract_json)
    return contract['abi']


def get_start_block_num():
    start_block_num = 0
    with open('block', 'r') as f:
        start_block_num = int(f.read())
    return start_block_num


def set_start_block_num(block_num: int):
    with open('block', 'w+') as f:
        f.write(str(block_num))


contarct = Contract('0x72Ca1aafE8E8f84ABbFba3705c35F084eCd21989',
                    'https://sync-testnet.vechain.org')

block = Block('https://sync-testnet.vechain.org')


event_abi_list = list(
    filter(lambda x: x.get('type', '') == 'event',
           get_abi_from_file('contract.json'))
)


def sync():
    print('开始同步, 请勿退出!')
    for event in contarct.get_events(get_start_block_num(), block.best_num(), event_abi_list):
        print(event)
        handle_event(event.name, event.args)
        set_start_block_num(event.block + 1)
    print('同步结束, 等待下次开始...')


def run_sync():
    queue = Task_Queue()
    task = Task(15, sync)
    queue.push(task)
    queue.start()


if __name__ == "__main__":
    run_sync()
