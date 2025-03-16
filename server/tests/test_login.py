import pytest
import os
import sys
import uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from controller.login import (
    check_username_exists, check_username_password, create_account,
    mark_client_connected, handle_login_request
)
from model.user import User
from unittest.mock import Mock

# ---------------- FIXTURES ---------------- #

@pytest.fixture
def sample_users():
    """
    Fixture to provide a sample dictionary of users.
    """
    return {
        "user1": User(username="Alice", password="secure123", uid="user1"),
        "user2": User(username="Bob", password="pass123", uid="user2", active=False),
        "user3": User(username="Charlie", password="qwerty", uid="user3")
    }

@pytest.fixture
def connected_clients():
    """
    Fixture to simulate connected clients dictionary.
    """
    return {}

@pytest.fixture
def mock_socket():
    """
    Fixture to mock a socket object.
    """
    return Mock()

@pytest.fixture
def mock_data():
    """
    Fixture to mock a data object with an address attribute.
    """
    data = Mock()
    data.addr = ("127.0.0.1", 5000)
    data.outb = b""
    return data

# ---------------- TESTS FOR CHECK FUNCTIONS ---------------- #

def test_check_username_exists(sample_users):
    """
    Test if check_username_exists() correctly identifies existing and non-existing usernames.
    """
    assert check_username_exists("Alice", sample_users) == "user1"
    assert check_username_exists("Bob", sample_users) is None  # Bob is inactive
    assert check_username_exists("NonExistentUser", sample_users) is None

def test_check_username_password(sample_users):
    """
    Test if check_username_password() correctly verifies user passwords.
    """
    assert check_username_password("user1", "secure123", sample_users) is True
    assert check_username_password("user1", "wrongpass", sample_users) is False
    assert check_username_password("user3", "qwerty", sample_users) is True

# ---------------- TESTS FOR ACCOUNT CREATION ---------------- #

def test_create_account(sample_users):
    """
    Test if create_account() successfully creates a new user and prevents duplicates.
    """
    new_uid = create_account("David", "newpass", sample_users)
    assert new_uid is not None
    assert "David" in [user.username for user in sample_users.values()]

    # Trying to create an existing username should return None
    assert create_account("Alice", "anotherpass", sample_users) is None

# ---------------- TESTS FOR CONNECTION TRACKING ---------------- #

def test_mark_client_connected(connected_clients, mock_socket):
    """
    Test if mark_client_connected() correctly registers a connected client.
    """
    uid = "user1"
    addr = ("127.0.0.1", 5000)

    mark_client_connected(uid, addr, connected_clients, mock_socket)

    assert uid in connected_clients
    assert connected_clients[uid] == [addr, mock_socket]

# ---------------- TESTS FOR LOGIN HANDLING ---------------- #

@pytest.mark.parametrize("task,username,password,expected_login_success", [
    ("login-password", "Alice", "secure123", True),  # Correct password
    ("login-password", "Alice", "wrongpass", False),  # Incorrect password
    ("login-password", "NonExistent", "newpass", True),  # Account created
])
def test_handle_login_request(mock_data, mock_socket, sample_users, connected_clients, task, username, password, expected_login_success):
    """
    Test handle_login_request() for both existing and new users.
    """
    message = {
        "task": task,
        "username": username,
        "password": password
    }

    handle_login_request(mock_data, mock_socket, message, sample_users, connected_clients, USE_WIRE_PROTOCOL=False)

    assert mock_data.outb != b""  # Some response should be sent

    response_str = mock_data.outb.decode("utf-8")
    assert f'"login_success": {str(expected_login_success).lower()}' in response_str  # Verify login success

# ---------------- EDGE CASES ---------------- #

def test_create_account_empty_password(sample_users):
    """
    Test that creating an account with an empty password is allowed (depends on business logic).
    """
    new_uid = create_account("NewUser", "", sample_users)
    assert new_uid is not None
    assert "NewUser" in [user.username for user in sample_users.values()]

def test_check_username_password_invalid_uid(sample_users):
    """
    Test that checking a password for an invalid user ID raises KeyError.
    """
    with pytest.raises(KeyError):
        check_username_password("invalid_uid", "password", sample_users)
