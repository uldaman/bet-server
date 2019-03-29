from peewee import *
from base_model import BaseModel


class Quiz(BaseModel):
    _id = IntegerField(index=True, unique=True, primary_key=True)
    gameName = FixedCharField(index=True)
    stage = IntegerField(index=True)
    startTime = BigIntegerField()

    leftLogo = FixedCharField()
    rightLogo = FixedCharField()
