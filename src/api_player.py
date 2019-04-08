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

        ps = Player.select(Player.player, Quiz._id, Quiz.gameName, Quiz.stage, Quiz.startTime, Quiz.leftLogo, Quiz.rightLogo)\
            .where(Player.player == args.pop('player'))\
            .join(Quiz)

        if 'stage' in args:
            ps = ps.where(Quiz.stage == args.pop('stage'))

        count = ps.count()
        data = ps.order_by(Quiz.startTime.desc())\
            .paginate(args.pop('page') + 1, args.pop('pagesize'))\
            .dicts()

        return {
            'count': count,
            'data': list(data)
        }
