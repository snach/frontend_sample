from mysql_connect import connect
from response import response_dict
import MySQLdb
from numconv import int2str


def create_post(date, thread, message, user, forum, is_approved, is_highlighted, is_spam, is_deleted, is_edited,
                parent):
    db = connect()
    cursor = db.cursor()
    try:
        path = ''
        if parent is None:
            is_root = 0
        else:
            is_root = 1
            cursor.execute("""SELECT path FROM posts WHERE id = %s""", (parent,))
            path = cursor.fetchone()

        cursor.execute("""INSERT INTO posts (date, thread, message, user, forum, isApproved, isHighlighted,
         isSpam, isDeleted, isEdited,parent,isRoot) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
         """, (date, thread, message, user, forum, is_approved, is_highlighted, is_spam, is_deleted, is_edited, parent,
               is_root))
        cursor.execute(""" SELECT * FROM posts WHERE forum=%s AND user=%s AND message=%s AND thread=%s """,
                       (forum, user, message, thread))
        db_id = cursor.fetchone()[0]
        results = {
            "code": 0,
            "response": {
                "date": date,
                "forum": forum,
                "id": db_id,
                "isApproved": is_approved,
                "isDeleted": is_deleted,
                "isEdited": is_edited,
                "isHighlighted": is_highlighted,
                "isSpam": is_spam,
                "message": message,
                "parent": parent,
                "thread": thread,
                "user": user
            }
        }
        post_id = cursor.lastrowid

        base36 = int2str(int(post_id), radix=36)
        path += str(len(base36)) + base36

        cursor.execute("""UPDATE posts SET path = %s WHERE id = %s""", (path, post_id))
        cursor.execute(""" SELECT count(*) FROM posts WHERE thread = %s and isDeleted = FALSE""", (thread,))
        posts_count = cursor.fetchone()[0]
        cursor.execute(""" UPDATE threads SET posts = %s  WHERE id = %s""", (str(posts_count), thread))
        print posts_count
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


def detail_post(related, post):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute("""SELECT * FROM posts WHERE id=%s """, (post,))
        db_id = cursor.fetchone()
        cursor.execute("""SELECT * FROM users WHERE email=%s""", (db_id["user"],))
        user_id = cursor.fetchone()
        cursor.execute(""" SELECT * FROM followers WHERE follower=%s""", (db_id["user"],))
        followers = cursor.fetchall()
        cursor.execute(""" SELECT * FROM followers WHERE followee=%s""", (db_id["user"],))
        following = cursor.fetchall()
        cursor.execute(""" SELECT thread FROM subscriptions WHERE user = %s""", (db_id['user'],))
        sub = cursor.fetchall()
        cursor.execute(""" SELECT * FROM forums WHERE short_name = %s""", (db_id["forum"],))
        forum = cursor.fetchone()
        cursor.execute(""" SELECT * FROM threads WHERE id = %s""", (db_id['id'],))
        thread = cursor.fetchone()
        cursor.execute(""" SELECT count(*) FROM posts WHERE thread = %s and isDeleted = FALSE""", (thread,))
        posts = cursor.fetchone()
        user_buf = db_id["user"]
        if "user" in related:
            user_buf = {
                "about": user_id["about"],
                "email": db_id["user"],
                "followers": followers,
                "following": following,
                "id": user_id['id'],
                "isAnonymous": bool(user_id["isAnonymous"]),
                "name": user_id['name'],
                "subscriptions": sub,
                "username": user_id['username']
            }

        forum_buf = db_id["forum"]
        if "forum" in related:
            forum_buf = {
                "id": forum['id'],
                "name": forum['name'],
                "short_name": forum['short_name'],
                "user": forum["user"]
            }

        thread_buf = db_id["thread"]
        if "thread" in related:
            thread_buf = {
                "date": str(thread["date"]),
                "dislikes": thread['dislikes'],
                "forum": thread['forum'],
                "id": thread['id'],
                "isClosed": bool(thread["isClosed"]),
                "isDeleted": bool(thread["isDeleted"]),
                "likes": thread["likes"],
                "message": thread["message"],
                "points": thread["points"],
                "posts": posts,
                "slug": thread["slug"],
                "title": thread["title"],
                "user": thread["user"]
            }

        results = {
            "code": 0,
            "response": {
                "date": str(db_id['date']),
                "dislikes": db_id["dislikes"],
                "forum": forum_buf,
                "id": db_id['id'],
                "isApproved": bool(db_id["isApproved"]),
                "isDeleted": bool(db_id["isDeleted"]),
                "isEdited": bool(db_id["isEdited"]),
                "isHighlighted": bool(db_id["isHighlighted"]),
                "isSpam": bool(db_id["isSpam"]),
                "likes": db_id["likes"],
                "message": db_id["message"],
                "parent": db_id["parent"],
                "points": int(db_id["points"]),
                "thread": thread_buf,
                "user": user_buf


            }
        }

        cursor.close()
        db.commit()
        db.close()
        return results
    except TypeError:
        return response_dict[1]

    except MySQLdb.IntegrityError as e:
        if e[0] == 1062:
            return response_dict[5]
        elif e[0] == 1452:
            return response_dict[1]
        else:
            return response_dict[4]


def list_post(since, order, limit, forum, thread):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        if thread is None and forum is None:
            return response_dict[3]
        if forum is not None:
            query = """SELECT * FROM posts WHERE forum = %s """
            query_params = (forum,)
        else:
            query = """SELECT * FROM posts WHERE thread = %s """
            query_params = (thread,)

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
                "forum": db_id['forum'],
                "id": db_id['id'],
                "isApproved": bool(db_id["isApproved"]),
                "isDeleted": bool(db_id["isDeleted"]),
                "isEdited": bool(db_id["isEdited"]),
                "isHighlighted": bool(db_id["isHighlighted"]),
                "isSpam": bool(db_id["isSpam"]),
                "likes": db_id["likes"],
                "message": db_id["message"],
                "parent": db_id["parent"],
                "points": int(db_id["points"]),
                "thread": db_id['thread'],
                "user": db_id['user']
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


def post_remove(post_id):
    db = connect()
    cursor = db.cursor()
    try:
        cursor.execute("""SELECT * FROM posts WHERE id=%s  """, (post_id,))
        del_sel = cursor.fetchone()
        if del_sel:
            cursor.execute("""UPDATE  posts SET isDeleted = TRUE  WHERE id=%s """, (post_id,))
            results = {
                "code": 0,
                "response": {
                    "post": post_id,
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


def post_restore(post_id):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute("""SELECT * FROM posts WHERE id=%s  """, (post_id,))
        del_sel = cursor.fetchone()
        if del_sel:
            cursor.execute("""UPDATE  posts SET isDeleted = FALSE  WHERE id=%s """, (post_id,))
            results = {
                "code": 0,
                "response": {
                    "post": post_id,
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


def post_update(post_id, message):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute("""SELECT * FROM posts WHERE id=%s  """, (post_id,))
        db_id = cursor.fetchone()
        if db_id:
            cursor.execute("""UPDATE  posts SET message=%s  WHERE id=%s """, (message, post_id))

            results = {
                "code": 0,
                "response": {
                    "date": str(db_id['date']),
                    "dislikes": db_id["dislikes"],
                    "forum": db_id['forum'],
                    "id": db_id['id'],
                    "isApproved": bool(db_id["isApproved"]),
                    "isDeleted": bool(db_id["isDeleted"]),
                    "isEdited": bool(db_id["isEdited"]),
                    "isHighlighted": bool(db_id["isHighlighted"]),
                    "isSpam": bool(db_id["isSpam"]),
                    "likes": db_id["likes"],
                    "message": message,
                    "parent": db_id["parent"],
                    "points": int(db_id["points"]),
                    "thread": db_id['thread'],
                    "user": db_id['user']
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


def post_vote(post_id, vote):
    db = connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute("""SELECT * FROM posts WHERE id=%s  """, (post_id,))
        is_id = cursor.fetchone()
        if is_id:
            print vote
            if vote == 1:
                cursor.execute("""UPDATE  posts SET likes=likes+1, points=points+1 WHERE id=%s """, (post_id,))
            elif vote == -1:
                cursor.execute("""UPDATE  posts SET dislikes=dislikes+1, points=points-1 WHERE id=%s """, (post_id,))
            else:
                return response_dict[3]

            cursor.execute("""SELECT * FROM posts WHERE id=%s  """, (post_id,))
            db_id = cursor.fetchone()
            results = {
                "code": 0,
                "response": {
                    "date": str(db_id['date']),
                    "dislikes": db_id["dislikes"],
                    "forum": db_id['forum'],
                    "id": db_id['id'],
                    "isApproved": bool(db_id["isApproved"]),
                    "isDeleted": bool(db_id["isDeleted"]),
                    "isEdited": bool(db_id["isEdited"]),
                    "isHighlighted": bool(db_id["isHighlighted"]),
                    "isSpam": bool(db_id["isSpam"]),
                    "likes": db_id["likes"],
                    "message": db_id["message"],
                    "parent": db_id["parent"],
                    "points": int(db_id["points"]),
                    "thread": db_id['thread'],
                    "user": db_id['user']
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
