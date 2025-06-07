import os
import sys
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import the database modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database.db_wrapper import (
    add_user,
    get_all_posts,
    get_user_by_username,
)


# Use mocking to avoid actual database operations
class TestDbWrapper:
    @patch("src.database.db_wrapper.db_pool")
    def test_add_user(self, mock_db_pool):
        # Setup mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Call the function
        add_user("testuser", "testpassword")

        # Verify the function called the database correctly
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_db_pool.putconn.assert_called_once_with(mock_conn)

    @patch("src.database.db_wrapper.db_pool")
    def test_get_user_by_username(self, mock_db_pool):
        # Setup mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, "testuser", "testpassword")

        # Call the function
        result = get_user_by_username("testuser")

        # Verify the result and function calls
        assert result == (1, "testuser", "testpassword")
        mock_cursor.execute.assert_called_once()
        mock_db_pool.putconn.assert_called_once_with(mock_conn)

    @patch("src.database.db_wrapper.db_pool")
    def test_get_all_posts(self, mock_db_pool):
        # Setup mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock posts with date_posted as a datetime
        import datetime

        mock_date = datetime.datetime.now()
        mock_posts = [
            {
                "post_id": 1,
                "author": "user1",
                "title": "Post 1",
                "content": "Content 1",
                "date_posted": mock_date,
            },
            {
                "post_id": 2,
                "author": "user2",
                "title": "Post 2",
                "content": "Content 2",
                "date_posted": mock_date,
            },
        ]
        mock_cursor.fetchall.return_value = mock_posts

        # Call the function
        get_all_posts()

        # Verify the function called the database correctly
        mock_cursor.execute.assert_called_once()
        mock_db_pool.putconn.assert_called_once_with(mock_conn)
