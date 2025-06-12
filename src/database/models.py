"""Models for the db"""

from datetime import datetime
from typing import TypedDict


class User(TypedDict):
    """
    represent a user obj from the db

    - user_id: int
    - username: str
    - hashed_pw: str
    """

    user_id: int
    username: str
    hashed_pw: str


class Post(TypedDict):
    """
    Represents a blog post entity from the database.

    - post_id (int): Unique identifier for the post
    - author (str): Username of the post author
    - title (str): Title of the blog post
    - content (str): Main content/body of the blog post
    - date_posted (datetime): Timestamp when the post was created
    - like_count (int): Number of likes the post has
    """

    post_id: int
    author: str
    title: str
    content: str
    date_posted: datetime
    like_count: int


class UserLikePostRecord(TypedDict):
    """
    Represents a record of a user liking a post.

    - user_id (int)
    - post_id (int)
    """

    user_id: int
    post_id: int
