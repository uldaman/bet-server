from request import Request, post
from decoder import EventDecoder
from typing import Dict, List


# TODO, 在 __init__ 时解析 abi
class Contract(object):

    def __init__(self, address: str, endpoint: str):
        self.address = address
        self.request = Request(endpoint)
        super(Contract, self).__init__()

    def get_events(self,
                   start_block_num: int,
                   to_block_num: int,
                   event_abi_list: List,
                   event_id: str = None) -> List:
        events = self._request_events(start_block_num, to_block_num, event_id)
        return list(
            filter(
                lambda x: x,
                map(
                    lambda x: self._decode_event(x, event_abi_list),
                    events)
            )
        )

    def _decode_event(self, event: Dict, event_abi_list: List) -> Dict:
        def _get_event_abi(event_id: str):
            return filter(lambda x: x.get('signature', '') == event_id, event_abi_list)

        for event_abi in _get_event_abi(event.get('topics', ['0x'])[0]):
            return EventDecoder(event_abi).decode_event(event)
        return None

    def _request_events(self,
                        start_block_num: int,
                        to_block_num: int,
                        event_id: str) -> List:
        query = {
            "range": {
                "unit": "block",
                "from": start_block_num,
                "to": to_block_num
            },
            "criteriaSet": [
                {
                    "address": self.address,
                    "topic0": event_id
                }
            ]
        }
        return self.request.logs.event.make_request(post, data=query)
