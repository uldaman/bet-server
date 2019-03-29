from peewee import Model, MySQLDatabase

mysql_db = MySQLDatabase('lol-match', user='root', password='root',)


class BaseModel(Model):

    '''A base model that will use our MySQL database'''
    class Meta:
        database = mysql_db
