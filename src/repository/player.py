from quiz import Quiz
from mongoengine import *
connect('lol-match')


class Player(Document):
    player = StringField(required=True)
    quiz = ReferenceField(Quiz, required=True)
    leftBet = IntField(default=0)
    rightBet = IntField(default=0)

    meta = {
        'strict': False,
        'indexes': [
            'player',
            {
                'fields': ('player', '-quiz'),
                'unique': True
            }
        ]
    }


if __name__ == "__main__":
    pass
    # player = Player(
    #     player='0x1',
    #     quiz=Quiz.objects(gameName='LPL').next(),
    #     bets=[{
    #         'amount': 100,
    #         'combatant': 1
    #     }]
    # )
    # player.save(force_insert=True)
    # for player in Player.objects(quiz=2):
    #     print(player.quiz)
