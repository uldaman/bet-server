from peewee import Model, MySQLDatabase

mysql_db = MySQLDatabase('lol-match', user='root', password='Hanxiao123!@#')


class BaseModel(Model):

    '''A base model that will use our MySQL database'''
    class Meta:
        database = mysql_db
