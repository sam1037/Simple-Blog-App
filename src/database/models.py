"""Models for the db"""

from typing import TypedDict
from datetime import datetime

class User(TypedDict):
    """
    represent a user obj from the db

    - user_id: int
    - username: str
    - password: str
    """
    user_id: int
    username: str
    password: str

class Post(TypedDict):
    """
    Represents a blog post entity from the database.
    
    - post_id (int): Unique identifier for the post
    - author (str): Username of the post author
    - title (str): Title of the blog post
    - content (str): Main content/body of the blog post
    - date_posted (datetime): Timestamp when the post was created
    """
    post_id: int
    author: str
    title: str
    content: str
    date_posted: datetime