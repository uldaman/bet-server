import json
import config
from event_handler import handle_event
from vecha import Contract
from task import Task, Task_Queue
from repository import mysql_db


mysql_db.init(config.database, user=config.user, password=config.password)


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


contarct = Contract(
    config.endpoint,
    config.contract,
    get_abi_from_file(config.abifile)
)


def sync():
    print('开始同步, 请勿退出!')
    for event in contarct.get_events(start_block_num=get_start_block_num()):
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
