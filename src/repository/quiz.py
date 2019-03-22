from mongoengine import *
from bet_updater import BetUpdater
connect('lol-match')


class Quiz(Document):
    _id = IntField(required=True, primary_key=True)
    startTime = IntField(required=True)
    stage = IntField(required=True)
    gameName = StringField(required=True)

    leftName = StringField(required=True)
    leftBet = StringField(default='0')
    leftScore = IntField(default=0)
    leftLogo = StringField(required=True)

    rightName = StringField(required=True)
    rightBet = StringField(default='0')
    rightScore = IntField(default=0)
    rightLogo = StringField(required=True)

    meta = {
        'strict': False,
        'queryset_class': BetUpdater,
        'indexes': ['gameName', 'stage',  ('gameName', '-stage')]
    }


if __name__ == "__main__":
    # for quiz in Quiz.objects(gameName='LPL'):
    #     print(quiz.rightName)
    print(Quiz.objects(gameName='LPL')[1:].to_json())
