from mysql_connect import connect
from response import response_dict
import MySQLdb


def create_thread(forum, title, is_closed, user, date, message, slug, is_deleted):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute("""INSERT INTO threads (forum,title,isClosed,user,date,message,slug,isDeleted) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
         """, (forum, title, is_closed, user, date, message, slug, is_deleted))
        cursor.execute(""" SELECT * FROM threads WHERE forum=%s AND user=%s AND title=%s""", (forum, user, title))
        db_id = cursor.fetchone()
        results = {
            "code": 0,
            "response": {
                "date": date,
                "forum": forum,
                "id": db_id['id'],
                "isClosed": bool(is_closed),
                "isDeleted": bool(db_id['isDeleted']),
                "message": message,
                "slug": slug,
                "title": title,
                "user": user,
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


def thread_subscribe(thread_id, follower_email):
    db = connect()
    cursor = db.cursor()
    try:
        cursor.execute("""INSERT INTO subscriptions (thread,user) VALUES (%s,%s)""",
                       (thread_id, follower_email))
        results = {
            "code": 0,
            "response": {
                "thread": thread_id,
                "user": follower_email,
            }
        }
        cursor.close()
        db.commit()
        db.close()
        return results
    except MySQLdb.IntegrityError as e:
        print e[0]
        if e[0] == 1062:
            return response_dict[5]
        elif e[0] == 1452:
            return response_dict[1]
        else:
            return response_dict[4]


def thread_unsubscribe(thread_id, follower_email):
    db = connect()
    cursor = db.cursor()
    try:
        cursor.execute("""SELECT * FROM subscriptions WHERE thread = %s AND user = %s """,
                       (thread_id, follower_email))
        dels = cursor.fetchone()
        print follower_email, thread_id
        if dels:
            cursor.execute("""DELETE FROM subscriptions WHERE thread = %s AND user = %s """,
                           (thread_id, follower_email))
            results = {
                "code": 0,
                "response": {
                    "thread": thread_id,
                    "user": follower_email,
                }
            }
            cursor.close()
            db.commit()
            db.close()
            return results
        else:
            return response_dict[1]
    except MySQLdb.IntegrityError:
        return response_dict[4]


def thread_remove(thread_id):
    db = connect()
    cursor = db.cursor()
    try:
        cursor.execute("""SELECT * FROM threads WHERE id = %s  """, (thread_id,))
        dels = cursor.fetchone()
        if dels:
            cursor.execute("""UPDATE posts SET isDeleted = TRUE WHERE thread = %s""", (thread_id,))
            cursor.execute("""UPDATE threads SET isDeleted= TRUE  WHERE id = %s """, (thread_id,))

            results = {
                "code": 0,
                "response": {
                    "thread": thread_id,
                }
            }
            cursor.close()
            db.commit()
            db.close()
            return results
        else:
            return response_dict[1]
    except MySQLdb.IntegrityError:
        return response_dict[4]


def thread_restore(thread_id):
    db = connect()
    cursor = db.cursor()
    try:
        cursor.execute("""SELECT * FROM threads WHERE id = %s  """, (thread_id,))
        dels = cursor.fetchone()
        if dels:
            cursor.execute("""UPDATE posts SET isDeleted = FALSE WHERE thread = %s""", (thread_id,))
            cursor.execute("""UPDATE  threads SET isDeleted = FALSE  WHERE id = %s """, (thread_id,))

            results = {
                "code": 0,
                "response": {
                    "thread": thread_id,
                }
            }
            cursor.close()
            db.commit()
            db.close()
            return results
        else:
            return response_dict[1]
    except MySQLdb.IntegrityError:
        return response_dict[4]


def thread_close(thread_id):
    db = connect()
    cursor = db.cursor()
    try:
        cursor.execute("""SELECT * FROM threads WHERE id = %s  """, (thread_id,))
        dels = cursor.fetchone()
        if dels:
            cursor.execute("""UPDATE  threads SET isClosed = TRUE  WHERE id=%s """, (thread_id,))

            results = {
                "code": 0,
                "response": {
                    "thread": thread_id,
                }
            }
            cursor.close()
            db.commit()
            db.close()
            return results
        else:
            return response_dict[1]
    except MySQLdb.IntegrityError:
        return response_dict[4]


def thread_open(thread_id):
    db = connect()
    cursor = db.cursor()
    try:
        cursor.execute("""SELECT * FROM threads WHERE id = %s  """, (thread_id,))
        dels = cursor.fetchone()
        if dels:
            cursor.execute("""UPDATE  threads SET isClosed = FALSE  WHERE id = %s """, (thread_id,))

            results = {
                "code": 0,
                "response": {
                    "thread": thread_id,
                }
            }
            cursor.close()
            db.commit()
            db.close()
            return results
        else:
            return response_dict[1]
    except MySQLdb.IntegrityError:
        return response_dict[4]


def detail_thread(related, thread):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute("""SELECT * FROM threads WHERE id = %s """, (thread,))
        db_id = cursor.fetchone()
        cursor.execute("""SELECT * FROM users WHERE email = %s""", (db_id['user'],))
        user_id = cursor.fetchone()
        cursor.execute(""" SELECT * FROM followers WHERE follower = %s""", (db_id['user'],))
        followers = cursor.fetchall()
        cursor.execute(""" SELECT * FROM followers WHERE followee = %s""", (db_id['user'],))
        following = cursor.fetchall()
        cursor.execute(""" SELECT thread FROM subscriptions WHERE user = %s""", (db_id['user'],))
        sub = cursor.fetchall()
        cursor.execute(""" SELECT * FROM forums WHERE `short_name` = %s""", (db_id['forum'],))
        forum = cursor.fetchone()
        cursor.execute(""" SELECT count(*) FROM posts WHERE thread = %s and isDeleted = FALSE""", (db_id['id'],))
        posts_count = cursor.fetchone()

        user_buf = db_id['user']
        if "user" in related:
            user_buf = {
                "about": user_id['about'],
                "email": db_id['user'],
                "followers": followers,
                "following": following,
                "id": user_id['id'],
                "isAnonymous": bool(user_id['isAnonymous']),
                "name": user_id['name'],
                "subscriptions": sub,
                "username": user_id['username']
            }
        forum_buf = db_id['forum']
        if "forum" in related:
            forum_buf = {
                "id": forum['id'],
                "name": forum['name'],
                "short_name": forum['short_name'],
                "user": forum['user']
            }
        results = {
            "date": str(db_id['date']),
            "dislikes": db_id['dislikes'],
            "forum": forum_buf,
            "id": db_id['id'],
            "isClosed": bool(db_id["isClosed"]),
            "isDeleted": bool(db_id["isDeleted"]),
            "likes": db_id["likes"],
            "message": db_id["message"],
            "points": db_id["points"],
            "posts": posts_count,
            "slug": db_id["slug"],
            "title": db_id["title"],
            "user": user_buf
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


def update_thread(thread_id, slug, message):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute("""UPDATE threads SET message = %s, slug = %s WHERE id = %s""", (message, slug, thread_id))
        cursor.execute(""" SELECT * FROM threads WHERE id = %s""", (thread_id,))
        db_id = cursor.fetchone()
        results = {
            "code": 0,
            "response": {
                "date": str(db_id['date']),
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


def list_thread(since, order, limit, forum, user):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        if user and forum:
            query = """SELECT * FROM threads WHERE forum = %s AND user = %s """
            query_params = (forum, user)
        elif forum:
            query = """SELECT * FROM threads WHERE forum = %s """
            query_params = (forum,)
        else:
            query = """SELECT * FROM threads WHERE user = %s """
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
            array.append(maps)
        print array
        result = {
            "code": 0,
            "response": array
        }
        return result

    except MySQLdb.Error:
        return response_dict[4]


def thread_vote(thread, vote):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute("""SELECT * FROM threads WHERE id = %s  """, (thread,))
        is_id = cursor.fetchone()
        if is_id:
            print vote
            if vote == 1:
                cursor.execute("""UPDATE threads SET likes = likes + 1, points = points + 1 WHERE id = %s """,
                               (thread,))
            elif vote == -1:
                cursor.execute("""UPDATE threads SET dislikes = dislikes + 1, points = points - 1 WHERE id = %s """,
                               (thread,))
            else:
                return response_dict[3]

            cursor.execute("""SELECT * FROM threads WHERE id = %s  """, (thread,))
            db_id = cursor.fetchone()
            results = {
                "code": 0,
                "response": {
                    "date": str(db_id['date']),
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
            }
            cursor.close()
            db.commit()
            db.close()
            return results
        else:
            return response_dict[1]
    except MySQLdb.IntegrityError:
        return response_dict[4]


def thread_post_list(since, order, limit, thread, sort):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        if thread is None:
            return response_dict[3]
        if sort is "flat":
            query = """SELECT * FROM posts WHERE thread = %s """
            query_params = (thread,)

            if since is not None:
                query += "AND date >= %s "
                query_params += (str(since),)

            query += "ORDER BY date " + order + " "

            if limit is not None:
                query += "LIMIT %s;"
                query_params += (int(limit),)

            cursor.execute(query, query_params)
            array = [i for i in cursor.fetchall()]
            for post in array:
                post.update({'date': str(post['date'])})

            result = {
                "code": 0,
                "response": array
            }
            return result
        else:
            subquery = """SELECT path
                    FROM posts
                    WHERE isRoot = TRUE AND thread = %s """
            query_params = (thread,)

            if since is not None:
                subquery += " AND date >= %s "
                query_params += (since,)

            if limit is not None:
                subquery += " ORDER BY path " + order + " LIMIT %s "
                query_params += (int(limit),)

            query = """SELECT *
                    FROM ( """ + subquery + """ ) as root
                    INNER JOIN posts as child
                    ON child.path LIKE CONCAT(root.path,'%%') """

            if since is not None:
                query += " WHERE child.date >= %s "
                query_params += (since,)

            query += " ORDER BY root.path " + order + ", child.path ASC "

            if sort == 'tree' and limit is not None:
                query += " LIMIT %s;"
                query_params += (int(limit),)

            try:
                cursor.execute(query, query_params)

            except MySQLdb.Error as e:
                print e
                return response_dict[3]

            array = [i for i in cursor.fetchall()]
            for post in array:
                post.update({'date': str(post['date'])})

            result = {
                "code": 0,
                "response": array
            }
            return result

    except MySQLdb.Error:
        return response_dict[4]
