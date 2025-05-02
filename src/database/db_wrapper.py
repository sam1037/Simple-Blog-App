# This file act as an layer btw the application logic layer and the actual database, so all the queries happen here

from src.database.db import db_pool
from psycopg2.extras import RealDictCursor
import pytz

def add_user(username: str, password: str) -> None:
    """
    add user to the db give username and pw
    """
    conn = db_pool.getconn()
    query = "INSERT INTO users(username, password) VALUES (%s, %s);"  
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (username, password))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error adding user: {e}");
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
        print(f"Error checking if username taken: {e}");
        return False
    finally:
        db_pool.putconn(conn)
    return False

# TODO change this to return a dict w/ realdictcursor
def get_user_by_username(username: str) -> tuple | None:
    """
    get user (username and pw) by username, return None if username not in db
    """
    conn = db_pool.getconn()
    query = "SELECT * FROM users where username = %s;"
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (username,))
            res = cursor.fetchone()
            return res
    except Exception as e:
        print(f"Error occured when getting user by username: {e}")
    finally:
        db_pool.putconn(conn)
    return None

def get_all_posts() -> list[dict] | None:
    """
    get all the posts as a dictionary, sort by date from newest to oldest
    """
    conn = db_pool.getconn()
    query = "SELECT * FROM posts ORDER BY date_posted DESC;"
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            res = cursor.fetchall()
            # handle the res, add local time
            hk_timezone = pytz.timezone('Asia/Hong_Kong')
            for post in res:
                utc_time = post['date_posted']
                hk_time = utc_time.replace(tzinfo=pytz.utc).astimezone(hk_timezone)
                post['date_posted'] = hk_time.strftime('%Y-%m-%d %H:%M') 
                print(hk_time)

            print(res)
            return res
    except Exception as e:
        print(f"Error occured when getting all posts from db: {e}")
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
        print(f"Error occured when inserting new post to db: {e}")
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
        print(f"Error occured when inserting new post to db: {e}")
        conn.rollback()
        return False
    finally:
        db_pool.putconn(conn)


def get_post_by_id(post_id: int) -> dict | None:
    """
    get a post by post_id, return a dictionary representing the post, or None if cannot find it
    """
    conn = db_pool.getconn()
    query = "SELECT * FROM posts WHERE post_id = %s;"
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (post_id,))
            res = cursor.fetchone()
            return res
    except Exception as e:
        print(f"Error occured when getting post by post_id: {e}")
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
        print(f"Error occured during deletion of a post by post id: {e}")
        conn.rollback()
        return False
    finally:
        db_pool.putconn(conn)