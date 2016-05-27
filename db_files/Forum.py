from mysql_connect import connect
from response import response_dict
from User import detail, func_followers, func_following, func_subscribe
from Thread import detail_thread
import MySQLdb


def status():
    try:
        db = connect()
        cursor = db.cursor()
        tables = ['users', 'threads', 'forums', 'posts']
        response = {}
        for table in tables:
            cursor.execute('SELECT COUNT(1) FROM %s' % table)
            db.commit()
            response[table] = cursor.fetchone()[0]
        db.close()
        result = {
            "code": 0,
            "response": response
        }
        cursor.close()
        db.commit()
        db.close()
        return result
    except MySQLdb.Error:
        return response_dict[4]


def clear():
    db = connect()
    cursor = db.cursor()
    try:
        cursor.execute("""SET foreign_key_checks = 0""")
        cursor.execute("""TRUNCATE forums""")
        cursor.execute("""TRUNCATE users""")
        cursor.execute("""TRUNCATE treads""")
        cursor.execute("""TRUNCATE posts""")
        cursor.execute("""TRUNCATE subscriptions""")
        cursor.execute("""TRUNCATE followers""")
        result = {
            "code": 0,
            "response": "OK"
        }
        cursor.close()
        db.commit()
        db.close()
        return result
    except MySQLdb.Error:
        return response_dict[4]


def create_forum(name, short_name, user):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute("""SELECT * FROM users WHERE email = %s""", (user,))
        cursor.execute("""INSERT INTO forums (name,short_name,user) VALUES (%s,%s,%s) """, (name, short_name, user))
        cursor.execute(""" SELECT id FROM forums WHERE name = %s """, (name,))
        db_id = cursor.fetchone()
        print db_id
        results = {
            "code": 0,
            "response": {
                "id": db_id['id'],
                "name": name,
                "short_name": short_name,
                "user": user
            }
        }
        cursor.close()
        db.commit()
        db.close()
        return results
    except MySQLdb.IntegrityError as e:
        if e[0] == 1062:
            return response_dict[5]
        elif e[0] == 1452:
            return response_dict[1]
        else:
            return response_dict[4]


def detail_forum(related, forum):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute("""SELECT * FROM forums WHERE short_name = %s """, (forum,))
        db_id = cursor.fetchone()
        cursor.execute("""SELECT * FROM users WHERE email = %s""", (db_id["user"],))
        user_id = cursor.fetchone()
        if related:
            results = {
                "id": db_id["id"],
                "name": db_id["name"],
                "short_name": db_id["short_name"],
                "user": {
                    "about": user_id["about"],
                    "email": db_id["user"],
                    "followers": func_followers(db_id["user"]),
                    "following": func_following(db_id["user"]),
                    "id": user_id["id"],
                    "isAnonymous": user_id["isAnonymous"],
                    "name": user_id["name"],
                    "subscriptions": func_subscribe(db_id["user"]),
                    "username": user_id["username"]
                }
            }
        else:
            results = {
                "id": db_id["id"],
                "name": db_id["name"],
                "short_name": db_id["short_name"],
                "user": db_id["user"]
            }
        cursor.close()
        db.commit()
        db.close()
        return results
    except MySQLdb.Error:
        return response_dict[1]
    except TypeError:
        return response_dict[1]
    except MySQLdb.IntegrityError as e:
        if e[0] == 1062:
            return response_dict[5]
        elif e[0] == 1452:
            return response_dict[1]
        else:
            return response_dict[4]


def post_list_forum(related, forum, order, since, limit):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        query = """SELECT * FROM posts WHERE forum = %s """
        query_params = (forum,)

        if since is not None:
            query += "AND date >= %s "
            query_params += (since,)
            query += "ORDER BY date " + order + " "

        if limit is not None:
            query += "LIMIT %s;"
            query_params += (int(limit),)

        cursor.execute(query, query_params)
        array = []
        for db_id in cursor.fetchall():
            maps = {
                "date": str(db_id["date"]),
                "dislikes": db_id["dislikes"],
                "forum": db_id["forum"],
                "id": db_id["id"],
                "isApproved": bool(db_id["isApproved"]),
                "isDeleted": bool(db_id["isDeleted"]),
                "isEdited": bool(db_id["isEdited"]),
                "isHighlighted": bool(db_id["isHighlighted"]),
                "isSpam": bool(db_id["isSpam"]),
                "likes": db_id["likes"],
                "message": db_id["message"],
                "parent": db_id["parent"],
                "points": int(db_id["points"]),
                "thread": db_id["thread"],
                "user": db_id["user"]
            }
            array.append(maps)
        #print array
        print related
        for iter in array:
            if 'user' in related:
                user = detail(iter['user'])
                iter.update({'user': user})

            if 'forum' in related:
                forum = detail_forum(None, iter['forum'])
                print forum
                iter.update({'forum': forum})

            if 'thread' in related:
                thread = detail_thread([], iter['thread'])
                iter.update({'thread': thread})

        results = {
            "code": 0,
            "response": array
        }
        cursor.close()
        db.commit()
        db.close()
        return results
    except MySQLdb.Error as e:
        print e
        return response_dict[1]
    #except TypeError as e:
    #    print e
    #    return response_dict[1]
    except MySQLdb.IntegrityError as e:
        if e[0] == 1062:
            return response_dict[5]
        elif e[0] == 1452:
            return response_dict[1]
        else:
            return response_dict[4]


def list_thread_forum(since, order, limit, forum, related):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        query = """SELECT * FROM threads WHERE forum = %s """
        query_params = (forum,)

        if since is not None:
            query += "AND date >= %s "
            query_params += (since,)
            query += "ORDER BY date " + order + " "

        if limit is not None:
            query += "LIMIT %s;"
            query_params += (int(limit),)

        cursor.execute(query, query_params)
        array = []
        for db_id in cursor.fetchall():
            maps = {
                #"date": str(db_id['date']),
                "dislikes": db_id["dislikes"],
                "forum": db_id["forum"],
                "id": db_id['id'],
                "isClosed": bool(db_id["isClosed"]),
                "isDeleted": bool(db_id["isDeleted"]),
                "likes": db_id["likes"],
                "message": db_id["message"],
                "points": db_id["points"],
                "posts": db_id["posts"],
                "slug": db_id["slug"],
                "title": db_id["title"],
                "user": db_id["user"]
            }
            maps.update({'date': str(db_id['date'])})
            array.append(maps)

        print array

        for iter in array:
            if 'user' in related:
                user = detail(iter['user'])
                iter.update({'user': user})

            if 'forum' in related:
                forum = detail_forum(None, iter['forum'])
                iter.update({'forum': forum})

        results = {
            "code": 0,
            "response": array
        }
        return results

    except MySQLdb.Error:
        return response_dict[4]

def list_user_forum(since_id, order, limit, forum):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:

        if since_id is None:
            since_id = " "
        else:
            since_id = " AND `id` >=  " + since_id

        if limit is None:
            limit = " "
        else:
            limit = ' LIMIT ' + limit

        cursor.execute("""SELECT * FROM users
            WHERE email IN (SELECT DISTINCT user FROM posts WHERE forum = %s)""" + since_id +
            " ORDER BY name " + order + limit + " ;", (forum,))
        array = []
        users = [i for i in cursor.fetchall()]
        for user in users:
            user = detail(user['email'])
            array.append(user)
        results = {"code": 0, "response": array}
        return results

    except MySQLdb.Error:
        return response_dict[4]
