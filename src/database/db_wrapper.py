"""This file act as an layer btw the application logic layer and the actual database, so all the queries happen here"""

import logging

import pytz
from passlib.hash import bcrypt
from psycopg2.extras import RealDictCursor

from src.database.db import db_pool
from src.database.models import Post, User, UserLikePostRecord

# TODO maybe add a with_db_connection decorator to abstract the repeating parts?

my_logger = logging.getLogger("my_flask_logger")


def add_user(username: str, password: str) -> None:
    """
    add user to the db give username and pw
    """
    hashed_pw = bcrypt.hash(password)

    conn = db_pool.getconn()
    query = "INSERT INTO users(username, hashed_pw) VALUES (%s, %s);"
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (username, hashed_pw))
        conn.commit()
    except Exception as e:
        conn.rollback()
        my_logger.error(f"Error adding user: {e}")
    finally:
        db_pool.putconn(conn)


def check_if_username_exist_in_db(username: str) -> bool:
    """
    check if username exist in db, returns a bool indicating the result
    """
    conn = db_pool.getconn()
    query = "SELECT 1 FROM users WHERE username = %s;"
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (username,))
            res = cursor.fetchone()
            return res is not None
    except Exception as e:
        my_logger.error(f"Error checking if username taken: {e}")
        return False
    finally:
        db_pool.putconn(conn)
    return False


def get_user_by_username(username: str) -> User | None:
    """
    get user (username and pw) by username, return None if username not in db
    """
    conn = db_pool.getconn()
    query = "SELECT * FROM users where username = %s;"
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (username,))
            res = cursor.fetchone()
            return res
    except Exception as e:
        my_logger.error(f"Error occured when getting user by username: {e}")
    finally:
        db_pool.putconn(conn)
    return None


# ? what type hint?
def get_current_user_liked_post_ids(user_id: int) -> list[int]:
    """ """
    conn = db_pool.getconn()
    query = "SELECT post_id FROM user_likes WHERE user_id = %s;"
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (user_id,))
            liked_posts_dicts = cursor.fetchall()
            return [post["post_id"] for post in liked_posts_dicts]
    except Exception as e:
        my_logger.error(f"Error occured: {e}")
        return []
    finally:
        db_pool.putconn(conn)


def get_all_posts() -> list[Post]:
    """
    get all the posts as a dictionary, sort by date from newest to oldest
    """
    conn = db_pool.getconn()
    # ? why left join
    query = """
        SELECT p.post_id, p.author, p.title, p.content, p.date_posted, COUNT(ul.user_id) AS like_count
        FROM posts p
        LEFT JOIN user_likes ul ON p.post_id = ul.post_id
        GROUP BY p.post_id, p.author, p.title, p.content, p.date_posted
        ORDER BY p.date_posted DESC;
    """
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            res = cursor.fetchall()
            # handle the res, add local time
            hk_timezone = pytz.timezone("Asia/Hong_Kong")
            for post in res:
                utc_time = post["date_posted"]
                hk_time = utc_time.replace(tzinfo=pytz.utc).astimezone(hk_timezone)
                post["date_posted"] = hk_time.strftime("%Y-%m-%d %H:%M")
            return res
    except Exception as e:
        my_logger.error(f"Error occured when getting all posts from db: {e}")
        return []
    finally:
        db_pool.putconn(conn)


def insert_new_post(author: str, title: str, content: str) -> bool:
    """
    insert a new post to db, return a Boolean indicating successful or not
    """
    conn = db_pool.getconn()
    query = "INSERT INTO posts(author, title, content) VALUES (%s, %s, %s);"
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (author, title, content))
        conn.commit()
        return True
    except Exception as e:
        my_logger.error(f"Error occured when inserting new post to db: {e}")
        conn.rollback()
        return False
    finally:
        db_pool.putconn(conn)


def edit_post_by_id(post_id: int, title: str, content: str) -> bool:
    """
    update a post by post id, return a boolean indicating successful or not
    """
    conn = db_pool.getconn()
    query = "UPDATE posts SET title=%s, content=%s WHERE post_id = %s;"
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (title, content, post_id))
        conn.commit()
        return True
    except Exception as e:
        my_logger.error(f"Error occured when inserting new post to db: {e}")
        conn.rollback()
        return False
    finally:
        db_pool.putconn(conn)


def get_post_by_id(post_id: int) -> Post | None:
    """
    get a post by post_id, return a dictionary representing the post, or None if cannot find it
    """
    conn = db_pool.getconn()
    query = """
        SELECT p.post_id, p.author, p.title, p.content, p.date_posted, COUNT(ul.user_id) AS like_count
        FROM posts p
        LEFT JOIN user_likes ul ON p.post_id = ul.post_id
        WHERE p.post_id = %s
        GROUP BY p.post_id, p.author, p.title, p.content, p.date_posted;
    """
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (post_id,))
            res = cursor.fetchone()
            return res
    except Exception as e:
        my_logger.error(f"Error occured when getting post by post_id: {e}")
    finally:
        db_pool.putconn(conn)
    return None


def delete_post_by_id(post_id: int) -> bool:
    """
    Delete a post given the post id, returns a Boolean indicating successful or not
    """
    conn = db_pool.getconn()
    query = "DELETE FROM posts WHERE post_id = %s;"
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (post_id,))
        conn.commit()
        return True
    except Exception as e:
        my_logger.error(f"Error occured during deletion of a post by post id: {e}")
        conn.rollback()
        return False
    finally:
        db_pool.putconn(conn)


def like_post(user_id: int, post_id: int) -> bool:
    """
    Save info of user liking a post, given user id and post id
    """
    conn = db_pool.getconn()
    query = "INSERT INTO user_likes(user_id, post_id) VALUES (%s, %s);"
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id, post_id))
        conn.commit()
        return True
    except Exception as e:
        my_logger.error(
            f"Error occured during saving info of user liking a post to db: {e}"
        )
        conn.rollback()
        return False
    finally:
        db_pool.putconn(conn)


def get_user_like_post_record(user_id: int, post_id: int) -> UserLikePostRecord | None:
    """
    find the user liking post record from table 'user_likes', return none if cannot find
    """
    conn = db_pool.getconn()
    query = "SELECT * FROM user_likes WHERE user_id = %s AND post_id = %s;"
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (user_id, post_id))
            res = cursor.fetchone()
            return res
    except Exception as e:
        my_logger.error(f"Error occured: {e}")
    finally:
        db_pool.putconn(conn)
    return None


def undo_like_post(user_id: int, post_id: int) -> bool:
    """
    Undo a user like a post, return a bool indicting sucessful or not
    """
    conn = db_pool.getconn()
    query = "DELETE FROM user_likes WHERE user_id = %s AND post_id = %s;"
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id, post_id))
        conn.commit()
        if cursor.rowcount > 0:
            return True  # Like was successfully undone
        else:
            return False  # Like didn't exist or no rows affected
    except Exception as e:
        my_logger.error(f"Error occured: {e}")
        conn.rollback()
        return False
    finally:
        db_pool.putconn(conn)
