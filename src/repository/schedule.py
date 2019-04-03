from peewee import *
from base_model import BaseModel


class Schedule(BaseModel):
    _id = IntegerField(index=True, unique=True, primary_key=True)
    startTime = BigIntegerField()
    gameName = FixedCharField()

    leftName = FixedCharField()
    leftScore = SmallIntegerField()
    leftLogo = FixedCharField()

    rightName = FixedCharField()
    rightScore = SmallIntegerField()
    rightLogo = FixedCharField()

    isOver = BooleanField()
