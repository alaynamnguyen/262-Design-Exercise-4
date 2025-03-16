import pytest
from unittest.mock import MagicMock
import grpc
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import chat_pb2
import chat_pb2_grpc

# ---------------- TEST FIXTURES ---------------- #

@pytest.fixture
def grpc_stub():
    """
    Fixture to provide a mock gRPC stub for testing.
    """
    stub = MagicMock(spec=chat_pb2_grpc.ChatServiceStub)

    stub.LoginUsername = MagicMock()
    stub.LoginPassword = MagicMock()

    return stub


# ---------------- TESTS FOR check_username() USING gRPC ---------------- #

def test_check_username_exists(grpc_stub):
    """
    Test if check_username() correctly identifies an existing user.
    """
    grpc_stub.LoginUsername.return_value = chat_pb2.LoginUsernameResponse(user_exists=True, username="Alice")

    request = chat_pb2.LoginUsernameRequest(username="Alice")
    response = grpc_stub.LoginUsername(request)

    grpc_stub.LoginUsername.assert_called_once_with(request)
    assert response.user_exists is True
    assert response.username == "Alice"


def test_check_username_not_exists(grpc_stub):
    """
    Test if check_username() correctly identifies a non-existent user.
    """
    grpc_stub.LoginUsername.return_value = chat_pb2.LoginUsernameResponse(user_exists=False, username="NonExistentUser")

    request = chat_pb2.LoginUsernameRequest(username="NonExistentUser")
    response = grpc_stub.LoginUsername(request)

    grpc_stub.LoginUsername.assert_called_once_with(request)
    assert response.user_exists is False
    assert response.username == "NonExistentUser"


# ---------------- TESTS FOR login_user() USING gRPC ---------------- #

def test_login_user_success(grpc_stub):
    """
    Test if login_user() correctly handles successful authentication.
    """
    grpc_stub.LoginPassword.return_value = chat_pb2.LoginPasswordResponse(success=True, uid="user123")

    request = chat_pb2.LoginPasswordRequest(username="Alice", password="valid_password_hash")
    response = grpc_stub.LoginPassword(request)

    grpc_stub.LoginPassword.assert_called_once_with(request)
    assert response.success is True
    assert response.uid == "user123"


def test_login_user_failure(grpc_stub):
    """
    Test if login_user() correctly handles failed authentication.
    """
    grpc_stub.LoginPassword.return_value = chat_pb2.LoginPasswordResponse(success=False, uid="")

    request = chat_pb2.LoginPasswordRequest(username="Alice", password="wrong_password_hash")
    response = grpc_stub.LoginPassword(request)

    grpc_stub.LoginPassword.assert_called_once_with(request)
    assert response.success is False
    assert response.uid == ""


# ---------------- TESTS FOR create_account() USING gRPC ---------------- #

def test_create_account_success(grpc_stub):
    """
    Test if create_account() correctly creates a new user account.
    """
    grpc_stub.LoginPassword.return_value = chat_pb2.LoginPasswordResponse(success=True, uid="new_user123")

    request = chat_pb2.LoginPasswordRequest(username="NewUser", password="new_password_hash")
    response = grpc_stub.LoginPassword(request)

    grpc_stub.LoginPassword.assert_called_once_with(request)
    assert response.success is True
    assert response.uid == "new_user123"


def test_create_account_failure(grpc_stub):
    """
    Test if create_account() correctly handles failed account creation.
    """
    grpc_stub.LoginPassword.return_value = chat_pb2.LoginPasswordResponse(success=False, uid="")

    request = chat_pb2.LoginPasswordRequest(username="NewUser", password="weak_password_hash")
    response = grpc_stub.LoginPassword(request)

    grpc_stub.LoginPassword.assert_called_once_with(request)
    assert response.success is False
    assert response.uid == ""


# ---------------- TEST FOR CLI LOGIN (Simulated) ---------------- #

def test_cli_login_existing_user(grpc_stub, monkeypatch):
    """
    Test if cli_login() successfully logs in an existing user.
    """
    monkeypatch.setattr("builtins.input", lambda _: "Alice")  # Simulate user input
    monkeypatch.setattr("builtins.input", lambda _: "secure123")

    grpc_stub.LoginPassword.return_value = chat_pb2.LoginPasswordResponse(success=True, uid="user123")

    request = chat_pb2.LoginPasswordRequest(username="Alice", password="secure123")
    response = grpc_stub.LoginPassword(request)

    grpc_stub.LoginPassword.assert_called_once_with(request)
    assert response.success is True
    assert response.uid == "user123"


def test_cli_login_new_user(grpc_stub, monkeypatch):
    """
    Test if cli_login() successfully creates a new user.
    """
    monkeypatch.setattr("builtins.input", lambda _: "NewUser")  # Simulate user input
    monkeypatch.setattr("builtins.input", lambda _: "newpassword")

    grpc_stub.LoginPassword.return_value = chat_pb2.LoginPasswordResponse(success=True, uid="new_user123")

    request = chat_pb2.LoginPasswordRequest(username="NewUser", password="newpassword")
    response = grpc_stub.LoginPassword(request)

    grpc_stub.LoginPassword.assert_called_once_with(request)
    assert response.success is True
    assert response.uid == "new_user123"
