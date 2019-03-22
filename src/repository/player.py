from quiz import Quiz
from mongoengine import *
from bet_updater import BetUpdater
connect('lol-match')


class Player(Document):
    meta = {}

    player = StringField(required=True)
    quiz = ReferenceField(Quiz, required=True)
    leftBet = StringField(default='0')
    rightBet = StringField(default='0')

    meta = {
        'strict': False,
        'queryset_class': BetUpdater,
        'indexes': [
            'player',
            {
                'fields': ('player', '-quiz'),
                'unique': True
            }
        ]
    }


if __name__ == "__main__":
    Player.objects(player='0x3', quiz=1).inc_bet('right', 10000)
