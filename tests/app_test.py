# TODO fix import and package man.

from unittest.mock import MagicMock, patch

import pytest

from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_login_page(client):
    """Test that the login page loads correctly"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"login" in response.data.lower()


def test_register_page(client):
    """Test that the register page loads correctly"""
    response = client.get("/register")
    assert response.status_code == 200
    assert b"register" in response.data.lower()


@patch("src.app.get_user_by_username")
@patch("src.app.add_user")
def test_register_new_user(mock_add_user, mock_get_user, client):
    """Test user registration with a new username"""
    mock_get_user.return_value = None
    response = client.post(
        "/register", data={"username": "newuser", "password": "password123"}
    )
    assert response.status_code == 200
    assert b"success" in response.data.lower()
    mock_add_user.assert_called_once_with("newuser", "password123")


@patch("src.app.get_user_by_username")
def test_login_success(mock_get_user, client):
    """Test successful login"""
    mock_get_user.return_value = [1, "testuser", "password123"]
    with client.session_transaction() as sess:
        pass

    response = client.post(
        "/",
        data={"username": "testuser", "password": "password123"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert sess["username"] == "testuser"


@patch("src.app.get_all_posts")
def test_get_posts(mock_get_all_posts, client):
    """Test the get_posts endpoint"""
    mock_posts = [
        {"id": 1, "title": "Test Post", "content": "Content", "author": "user1"}
    ]
    mock_get_all_posts.return_value = mock_posts

    response = client.get("/get_posts")

    assert response.status_code == 200
    assert response.json == mock_posts
