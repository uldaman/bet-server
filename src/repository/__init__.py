import sys
import os

sys.path.append(os.path.split(os.path.realpath(__file__))[0])


from base_model import mysql_db  # noqa
from quiz import Quiz  # noqa
from player import Player  # noqa
