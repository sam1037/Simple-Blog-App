# This file act as an layer btw the application logic layer and the actual database

from database.db import db_pool

# add user give username and pw
def add_user(username, password):
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

def check_if_username_exist_in_db(username):
    conn = db_pool.getconn()
    query = "SELECT 1 FROM users WHERE username = %s;"  
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (username,))
            res = cursor.fetchone()
            #print(res, type(res), len(res))
            return res is not None
    except Exception as e:
        print(f"Error checking if username taken: {e}");
    finally:
        db_pool.putconn(conn)
    return True

# get user (username and pw) by username, return None if username not in db
def get_user_by_username(username):
    conn = db_pool.getconn()
    query = "SELECT * FROM users where username = %s;"
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (username,))
            res = cursor.fetchone()
            #print(res, type(res), len(res))
            return res
    except Exception as e:
        print(f"Error occurred when getting user by username: {e}")
    finally:
        db_pool.putconn(conn)
    return None