import json
from flask_restful import Resource, reqparse
from repository import Quiz


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
        page = args.pop('page')
        pagesize = args.pop('pagesize')
        offset = page * pagesize
        quiz = Quiz.objects(
            **args).order_by('-startTime')[offset:offset+pagesize].to_json()
        return json.loads(quiz)


class QuizAPI(Resource):

    def __init__(self):
        super(QuizAPI, self).__init__()

    def get(self, uid):
        quiz = Quiz.objects(_id=uid).first()
        if quiz:
            return json.loads(quiz.to_json())
        return {}
