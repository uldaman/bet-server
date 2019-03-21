from request import Request, post
from decoder import EventDecoder
from typing import Dict, Iterable


class Contract(object):

    def __init__(self, address: str, endpoint: str):
        self.address = address
        self.request = Request(endpoint)
        super(Contract, self).__init__()

    def get_events(self, start_block_num: int, to_block_num: int, event_abi: Dict) -> Iterable:
        decoder = EventDecoder(event_abi)
        query = {
            "range": {
                "unit": "block",
                "from": start_block_num,
                "to": to_block_num
            },
            "criteriaSet": [
                {
                    "address": self.address,
                    "topic0": event_abi['signature']
                }
            ]
        }
        events = self.request.logs.event.make_request(post, data=query)
        return map(lambda x: decoder.decode_event(x['topics'], x['data']), events)
