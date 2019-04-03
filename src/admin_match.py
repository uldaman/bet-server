import json
from flask_restful import Resource, reqparse
from repository import get_dict_from_cursor, mysql_db


class MatchAdmin(Resource):

    def __init__(self):
        super(MatchAdmin, self).__init__()

        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'page', type=int, location='args', required=True, help='No page provided')
        self.reqparse.add_argument(
            'pagesize', type=int, location='args', required=True, help='No pagesize provided')
        self.reqparse.add_argument(
            'type', type=int, location='args', required=True, help='No type provided')

    def get(self):
        args = self.reqparse.parse_args()

        if args['type'] == 0:  # pending start quiz
            r = mysql_db.execute_sql('''
                select * from `schedule` where
                (select count(1) from `quiz` where quiz._id=schedule._id) = 0 and
                schedule.isOver = 0
                ''')
            return get_dict_from_cursor(r)
        elif args['type'] == 1:  # started quiz
            r = mysql_db.execute_sql('''
                select * from `schedule` where
                (select count(1) from `quiz` where quiz._id=schedule._id) > 0 and
                schedule.isOver = 0
            ''')
            return get_dict_from_cursor(r)
        elif args['type'] == 2:  # overed quiz
            r = mysql_db.execute_sql('''
                select * from `schedule` where
                (select count(1) from `quiz` where quiz._id=schedule._id and quiz.stage<3) > 0 and
                schedule.isOver = 1
            ''')
            return get_dict_from_cursor(r)
        else:  # finish quiz
            r = mysql_db.execute_sql('''
                select * from `schedule` where
                (select count(1) from `quiz` where quiz._id=schedule._id and quiz.stage=3) > 0 and
                schedule.isOver = 1
            ''')
            return get_dict_from_cursor(r)
