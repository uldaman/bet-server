from peewee import Model, MySQLDatabase


# mysql_db must be inited externally
mysql_db = MySQLDatabase(None)


class BaseModel(Model):

    '''A base model that will use our MySQL database'''
    class Meta:
        database = mysql_db
