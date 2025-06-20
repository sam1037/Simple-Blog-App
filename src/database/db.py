"""This file handles connection to the postgresql database and db table schemas."""

import os

import click
from dotenv import load_dotenv
from psycopg2 import pool

# Load environment variables once
load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

# Create the pool ONCE at the module level
db_pool = pool.SimpleConnectionPool(1, 10, DATABASE_URL)


def test_db_connection() -> None:
    """test if the db is connected or not, print "DB connection good" if connected."""
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(result)
            print("DB connection good")
    finally:
        db_pool.putconn(conn)


def end_db_connection():
    db_pool.closeall()


def drop_all() -> None:
    """Drop all data and tables"""
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS posts CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS users CASCADE;")
        conn.commit()
    finally:
        db_pool.putconn(conn)


# TODO
def seed_db():
    print("TODO seed db")


def init_db() -> None:
    """create the tables if don't exist, seed the data if any, won't remove existing data"""
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cursor:
            with open("src/database/schema.sql", "r") as f:
                sql = f.read()
                cursor.execute(sql)  # For single statement or small scripts
        conn.commit()
        seed_db()
    finally:
        db_pool.putconn(conn)


@click.command("init-db")
def init_db_cmd() -> None:
    """Create the tables if don't exist, seed the data if any"""
    click.echo("init-db cmd called")
    init_db()
