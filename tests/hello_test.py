import src.database.db_wrapper as db_wrapper
import pytest
from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_greeting():
    print("Hello, world!")


def test_checkout():
    print("This is checkout")


def logout():
    print("This is logout")


def test_logout():
    logout()


def test_dummy():
    assert 1 + 1 == 2


def my_sum(lst: list[int]) -> int:
    return sum(lst)


# test regsiter a new user
def test_register(client):
    TEST_USERNAME = "test_alpha_beta"

    # act
    response = client.post(
        "/register", data={"username": TEST_USERNAME, "password": "pw"}
    )

    # assert
    assert response.status_code in (200, 400)
    assert db_wrapper.get_user_by_username(TEST_USERNAME) is not None


my_sum([1, 2, 3, 5])
