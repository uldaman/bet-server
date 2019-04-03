from peewee import Model, MySQLDatabase


# mysql_db must be inited externally
mysql_db = MySQLDatabase(None)


class BaseModel(Model):

    '''A base model that will use our MySQL database'''
    class Meta:
        database = mysql_db


def get_dict_from_cursor(cursor):
    ncols = len(cursor.description)
    colnames = [cursor.description[i][0] for i in range(ncols)]
    results = []

    for row in cursor.fetchall():
        res = {}
        for i in range(ncols):
            res[colnames[i]] = row[i]
        results.append(res)

    return results
