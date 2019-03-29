import json
from flask_restful import Resource, reqparse
from repository import Quiz
from peewee import DoesNotExist


class QuizsAPI(Resource):

    def __init__(self):
        super(QuizsAPI, self).__init__()

        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'page', type=int, location='args', required=True, help='No page provided')
        self.reqparse.add_argument(
            'pagesize', type=int, location='args', required=True, help='No pagesize provided')
        self.reqparse.add_argument(
            'stage', type=int, location='args', store_missing=False)
        self.reqparse.add_argument(
            'gameName', type=str, location='args', store_missing=False)

    def get(self):
        args = self.reqparse.parse_args()

        qs = Quiz.select()\
            .order_by(Quiz.startTime)\
            .paginate(args.pop('page') + 1, args.pop('pagesize'))\
            .dicts()

        if 'stage' in args:
            qs = qs.where(Quiz.stage == args.pop('stage'))

        if 'gameName' in args:
            qs = qs.where(Quiz.gameName == args.pop('gameName'))

        return list(qs)


class QuizAPI(Resource):

    def __init__(self):
        super(QuizAPI, self).__init__()

    def get(self, uid):
        try:
            return Quiz.select().where(Quiz._id == uid).dicts().get()
        except DoesNotExist:
            return {}
