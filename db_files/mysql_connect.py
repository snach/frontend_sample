import MySQLdb

host = "localhost"
user = "root"
password = "rootPassword"
db = "forum"


def connect():
    con = MySQLdb.connect(host=host, user=user, passwd=password, db=db, use_unicode=True, charset="utf8")
    return con
