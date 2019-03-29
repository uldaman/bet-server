from peewee import *
from base_model import BaseModel
from quiz import Quiz


class Player(BaseModel):
    player = FixedCharField(index=True)
    quiz = ForeignKeyField(Quiz, db_column='quiz', field=Quiz._id)

    class Meta:
        primary_key = CompositeKey('player', 'quiz')
