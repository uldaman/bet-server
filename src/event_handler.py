from repository import Quiz, Player
from enum import Enum, unique
from peewee import IntegrityError


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
        '_join': lambda: _handle_join_event(event)
    }
    if name in handle_mapping:
        handle_mapping[name]()


def _handle_creat_event(event):
    def logo_path(x): return '/static/img/{}.png'.format(x.lower())
    try:
        Quiz.create(**event, stage=Stage.Active.value,
                    leftLogo=logo_path(event['leftName']),
                    rightLogo=logo_path(event['rightName']))
    except IntegrityError:
        print('This id quiz is already exists')


def _update_stage(event, new_stage):
    quiz = Quiz.get_or_none(Quiz._id == event['_id'])
    if quiz:
        quiz.stage = new_stage
        quiz.save()


def _handle_join_event(event):
    try:
        Player.create(
            player=event['player'],
            quiz=event['_id']
        )
    except IntegrityError:
        print('Player has already joined this quiz')
