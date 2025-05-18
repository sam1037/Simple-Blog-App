# Test my flask app

import pytest
from src.app import app
import src.database.db_wrapper as db_wrapper

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# test can reach the login page
def test_login_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b'login' in response.data.lower()

# test can reach the register page
def test_register_page(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b'register' in response.data.lower()

# test regsiter a new user
def test_register(client):
    # arrange: clean up db first, maybe later will do the best approach
    TEST_USERNAME = "test_alpha_beta"
    user = db_wrapper.get_user_by_username(TEST_USERNAME)
    if user:
        db_wrapper.delete_user_by_id(user['user_id'])

    # act
    response = client.post("/register", data = {
        'username': TEST_USERNAME,
        'password': 'pw'
    })

    # assert
    assert response.status_code == 200
    assert db_wrapper.get_user_by_username(TEST_USERNAME) is not None

    # clean up
    user = db_wrapper.get_user_by_username(TEST_USERNAME)
    if user:
        db_wrapper.delete_user_by_id(user['user_id'])

# test login an exisitng acc
def test_login():
    pass

def test_new_post():
    pass

def test_edit_post():
    pass

def test_get_posts():
    pass

def test_delete_post():
    pass