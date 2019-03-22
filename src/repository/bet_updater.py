from mongoengine import QuerySet
from typing import Callable


class BetUpdater(QuerySet):
    def inc_bet(self, left_right: str, inc: int):
        if not self._update_bet(_inc_bet, left_right, inc):
            self.update_one(upsert=True, **_new_bet(left_right, inc))

    def dec_bet(self, left_right: str, dec: int):
        self._update_bet(_dec_bet, left_right, dec)

    def _update_bet(self, fn: Callable[[int, int], int], left_right: str, bet: int) -> bool:
        obj = self.first()
        if obj:
            old_bet = int(obj['{}Bet'.format(left_right)])
            obj.update(**_new_bet(left_right, fn(old_bet, bet)))
            return True
        return False


def _new_bet(left_right: str, bet: int):
    return {
        'set__{}Bet'.format(left_right): str(bet)
    }


def _inc_bet(old_bet: int, inc: int) -> str:
    return str(old_bet + inc)


def _dec_bet(old_bet: int, dec: int) -> str:
    return str(old_bet - dec)
