from repository import Quiz, Player


def handle_event(name, event):
    handle_mapping = {
        '_creat': lambda: _handle_creat_event(event),
        '_cancel': lambda: _update_stage(event, 3),
        '_lock': lambda: _update_stage(event, 2),
        '_finish': lambda: _update_stage(event, 4),
        '_join': lambda: _update_bet(event, 'inc'),
        '_repent': lambda: _update_bet(event, 'dec')
    }
    if name in handle_mapping:
        handle_mapping[name]()


def _handle_creat_event(event):
    def logo_path(x): return '/static/img/{}.png'.format(x.lower())
    quiz = Quiz(**event, stage=1,
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
    quiz = Quiz.objects(_id=event['_id'])
    player = Player.objects(player=event['player'], quiz=event['_id'])
    left_right = 'left' if event['combatant'] == 1 else 'right'
    new_bet = {
        '{}__{}Bet'.format(dec_inc, left_right): event['stakes'] / pow(10, 18)
    }
    player.upsert_one(**new_bet)
    quiz.update(**new_bet)
