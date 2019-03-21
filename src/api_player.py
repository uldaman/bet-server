import json
from flask_restful import Resource, reqparse
from repository import Quiz, Player


class PlayerAPI(Resource):

    def __init__(self):
        super(PlayerAPI, self).__init__()

        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'page', type=int, location='args', required=True, help='No page provided')
        self.reqparse.add_argument(
            'pagesize', type=int, location='args', required=True, help='No pagesize provided')
        self.reqparse.add_argument(
            'player', type=str, location='args', required=True, help='No player address provided')
        self.reqparse.add_argument(
            'stage', type=int, location='args', store_missing=False)

    def get(self):
        args = self.reqparse.parse_args()
        page = args.pop('page')
        pagesize = args.pop('pagesize')
        offset = page * pagesize
        if 'stage' in args:
            stage = args.pop('stage')
            args['quiz__in'] = Quiz.objects(stage=stage)
        result = []
        for player in Player.objects(**args)[offset:offset+pagesize]:
            quiz = json.loads(player.quiz.to_json())
            player = json.loads(player.to_json())
            player['quiz'] = quiz
            del player['_id']
            result.append(player)
        return result
