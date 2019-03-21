# -*- coding:utf-8 -*-
from api_quiz import QuizsAPI, QuizAPI
from api_player import PlayerAPI
from flask import Flask
from flask_restful import Api
from flask_cors import CORS

app = Flask(__name__, static_url_path='/static')
api = Api(app)
CORS(app, supports_credentials=True)

api.add_resource(QuizsAPI, '/api/quizs', endpoint='quizs')
api.add_resource(QuizAPI, '/api/quiz/<int:uid>', endpoint='quiz')

api.add_resource(PlayerAPI, '/api/player', endpoint='player')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
