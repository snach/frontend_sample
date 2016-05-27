from mysql_connect import connect
from response import response_dict
import MySQLdb


def create(username, about, name, email, is_anon):
    db = connect()
    cursor = db.cursor()
    try:
        cursor.execute("""INSERT INTO users (username,name,email,isAnonymous,about) VALUES (%s,%s,%s,%s,%s) """,
                       (username, name, email, is_anon, about))
        cursor.execute(""" SELECT id FROM users WHERE email=%s """, (email,))
        db_id = cursor.fetchone()
        results = {
            "code": 0,
            "response": {
                "about": about,
                "email": email,
                "id": db_id[0],
                "isAnonymous": bool(is_anon),
                "name": name,
                "username": username
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
            print e
            return response_dict[4]

    except MySQLdb.Error as e:
        print e
        results = response_dict[4]
        return results


def detail(email):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        email = email.replace("%40", "@")
        print email
        cursor.execute(""" SELECT * FROM users WHERE email=%s""", (email,))
        str = cursor.fetchone()
        if not str:
            return response_dict[1]
        else:
            print str
            results = {
                "about": str["about"],
                "email": str["email"],
                "followers": func_followers(email),
                "following": func_following(email),
                "id": str['id'],
                "isAnonymous": bool(str['isAnonymous']),
                "name": str['name'],
                "subscriptions": func_subscribe(email),
                "username": str['username']
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
            print e
            return response_dict[4]


def func_subscribe(email):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(""" SELECT thread FROM subscriptions WHERE user=%s""", (email,))
    subscribe = [i['thread'] for i in cursor.fetchall()]
    cursor.close()
    db.commit()
    db.close()
    print subscribe
    return subscribe


def follow(follower, followee):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute(""" SELECT * FROM users WHERE email=%s""", (followee,))
        str = cursor.fetchone()
        cursor.execute(""" SELECT * FROM users WHERE email=%s""", (follower,))
        str2 = cursor.fetchone()
        if str2:
            cursor.execute("""INSERT INTO followers (follower ,followee ) VALUES (%s,%s) """, (follower, followee))
            cursor.execute(""" SELECT followee  FROM followers WHERE follower = %s""", (follower,))
            followers = cursor.fetchall()
            cursor.execute(""" SELECT follower  FROM followers WHERE followee = %s""", (follower,))
            following = cursor.fetchall()
            cursor.execute(""" SELECT count(*) FROM subscriptions WHERE user = %s""", (followee,))
            count_subscribe = cursor.fetchone()

            print str
            results = {
                "code": 0,
                "response": {
                    "about": str['about'],
                    "email": str['email'],
                    "followers": func_followers(follower),
                    "following": func_following(follower),
                    "id": str['id'],
                    "isAnonymous": bool(str['isAnonymous']),
                    "name": str['name'],
                    "subscriptions": count_subscribe,
                    "username": str['username']
                }
            }
            cursor.close()
            db.commit()
            db.close()
            return results
        else:
            return response_dict[1]

    except MySQLdb.IntegrityError as e:
        if e[0] == 1062:
            return response_dict[5]
        elif e[0] == 1452:
            return response_dict[1]
        else:
            return response_dict[4]
    except TypeError as e:
        print e
        results = response_dict[1]
        return results


def func_followers(email):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(""" SELECT followee FROM followers WHERE follower = %s """, (email,))
    followers = [i['followee'] for i in cursor.fetchall()]
    cursor.close()
    db.commit()
    db.close()
    print followers
    return followers


def func_following(email):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(""" SELECT follower FROM followers WHERE followee = %s """, (email,))
    following = [i['follower'] for i in cursor.fetchall()]
    cursor.close()
    db.commit()
    db.close()
    print following
    return following


def list_followers(email, order, limit, since_id):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute(""" SELECT * FROM users WHERE email = %s""", (email,))
        if email is None:
            return response_dict[1]

        if limit is None:
            limit = " "
        else:
            limit = ' LIMIT ' + limit

        try:
            cursor.execute(
                """SELECT about, email, id, isAnonymous, name, username FROM followers AS f
                    JOIN users ON users.email = f.followeee
                    WHERE f.follower = %s AND users.id >= %s
                    ORDER BY name """ + order + limit + " ;",
                (
                    email,
                    int(since_id)
                )
            )
        except MySQLdb.Error as e:
            print e
            return response_dict[3]
        users = [i for i in cursor.fetchall()]
        for user in users:
            following = func_following(user['email'])
            followers = func_followers(user['email'])

            cursor.execute(
                """SELECT `thread`
                    FROM `subscriptions`
                    WHERE `user` = %s;""",
                (
                    user['email'],
                )
            )
            threads = [i['thread'] for i in cursor.fetchall()]
            user.update({'following': following, 'followers': followers, 'subscriptions': threads})
        if users:
            results = {"code": 0, "response": users}
            return results
        else:
            return response_dict[1]
    except MySQLdb.IntegrityError as e:
        if e[0] == 1062:
            return response_dict[5]
        elif e[0] == 1452:
            return response_dict[1]
        else:
            return response_dict[4]


def list_following(email, order, limit, since_id):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute(""" SELECT * FROM users WHERE email=%s""", (email,))
        if email is None:
            return response_dict[1]

        if limit is None:
            limit = " "
        else:
            limit = ' LIMIT ' + limit

        try:
            cursor.execute(
                """SELECT about, email, id, isAnonymous, name, username FROM followers AS f
                    JOIN users ON users.email = f.follower
                    WHERE f.followee = %s AND users.id >= %s
                    ORDER BY name """ + order + limit + " ;", (email, int(since_id))
            )
        except MySQLdb.Error as e:
            print e
            return response_dict[3]
        users = [i for i in cursor.fetchall()]
        for user in users:
            following = func_following(user['email'])
            followers = func_followers(user['email'])

            cursor.execute(
                """SELECT thread
                    FROM subscriptions
                    WHERE user = %s;""",
                (
                    user['email'],
                )
            )
            threads = [i['thread'] for i in cursor.fetchall()]
            user.update({'following': following, 'followers': followers, 'subscriptions': threads})
            if users:
                results = {"code": 0, "response": users}
                return results
            else:
                return response_dict[1]
    except MySQLdb.IntegrityError as e:
        if e[0] == 1062:
            return response_dict[5]
        elif e[0] == 1452:
            return response_dict[1]
        else:
            return response_dict[4]


def profile_update(about, user, name):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute(""" UPDATE users SET name = %s, about = %s WHERE email = %s""", (name, about, user))
        cursor.execute(""" SELECT * FROM users WHERE email = %s""", (user,))
        str = cursor.fetchone()

        print str
        results = {
            "code": 0,
            "response": {
                "about": str['about'],
                "email": str['email'],
                "followers": func_followers(user),
                "following": func_following(user),
                "id": str['id'],
                "isAnonymous": bool(str['isAnonymous']),
                "name": str['name'],
                "subscriptions": func_subscribe(user),
                "username": str['username']
            }
        }
        cursor.close()
        db.commit()
        db.close()
        return results
    except MySQLdb.IntegrityError as e:
        return response_dict[4]


def unfollow(follower, followee):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute(""" SELECT * FROM users WHERE email=%s""", (followee,))
        str = cursor.fetchone()
        cursor.execute(""" SELECT * FROM users WHERE email=%s""", (follower,))
        str2 = cursor.fetchone()
        if str2:
            cursor.execute("""DELETE FROM followers WHERE follower = %s AND followee = %s """, (follower, followee))

            print str
            results = {
                "code": 0,
                "response": {
                    "about": str['about'],
                    "email": str['email'],
                    "followers": func_followers(follower),
                    "following": func_following(follower),
                    "id": str['id'],
                    "isAnonymous": bool(str['isAnonymous']),
                    "name": str['name'],
                    "subscriptions": func_subscribe(follower),
                    "username": str['username']
                }
            }
            cursor.close()
            db.commit()
            db.close()
            return results
        else:
            return response_dict[1]

    except MySQLdb.IntegrityError as e:
        if e[0] == 1062:
            print e
            return response_dict[5]
        elif e[0] == 1452:
            return response_dict[1]
        else:
            return response_dict[4]
    except TypeError:
        results = response_dict[1]
        return results


def user_post_list(user, order, since, limit):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        query = """SELECT * FROM posts WHERE user = %s """
        query_params = (user,)

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
                "date": str(db_id['date']),
                "dislikes": db_id['dislikes'],
                "forum": db_id['forum'],
                "id": db_id['id'],
                "isApproved": bool(db_id['isApproved']),
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
        print array

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
    except TypeError as e:
        print e
        return response_dict[1]
    except MySQLdb.IntegrityError as e:
        if e[0] == 1062:
            return response_dict[5]
        elif e[0] == 1452:
            print e
            return response_dict[1]
        else:
            return response_dict[4]
