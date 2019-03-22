from repository import Quiz, Player
from enum import Enum, unique


@unique
class Stage(Enum):
    Active = 1
    Locked = 2
    Canceled = 3
    Finished = 4


def handle_event(name, event):
    handle_mapping = {
        '_creat': lambda: _handle_creat_event(event),
        '_cancel': lambda: _update_stage(event, Stage.Canceled.value),
        '_lock': lambda: _update_stage(event, Stage.Locked.value),
        '_finish': lambda: _update_stage(event, Stage.Finished.value),
        '_join': lambda: _update_bet(event, 'inc_bet'),
        '_repent': lambda: _update_bet(event, 'dec_bet')
    }
    if name in handle_mapping:
        handle_mapping[name]()


def _handle_creat_event(event):
    def logo_path(x): return '/static/img/{}.png'.format(x.lower())
    quiz = Quiz(**event, stage=Stage.Active.value,
                leftLogo=logo_path(event['leftName']),
                rightLogo=logo_path(event['rightName']))
    try:
        quiz.save(force_insert=True)
    except:
        print('This id quiz is already exists')


def _update_stage(event, new_stage):
    quiz = Quiz.objects(_id=event['_id'])
    quiz.update_one(set__stage=new_stage)


def _update_bet(event, dec_inc):
    def _update(obj): getattr(obj, dec_inc)(left_right, event['stakes'])

    left_right = 'left' if event['combatant'] == 1 else 'right'

    quiz = Quiz.objects(_id=event['_id'])
    _update(quiz)

    player = Player.objects(player=event['player'], quiz=event['_id'])
    _update(player)
