import pytest
import json
import hashlib
import sys 
import os
from unittest.mock import Mock, patch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import (
    json_to_wire_protocol, wire_protocol_to_json,
    send_request, receive_response, hash_password
)

# ---------------- TESTS FOR JSON <-> WIRE PROTOCOL ---------------- #

@pytest.mark.parametrize("json_message, expected_wire", [
    ({"task": "login-username", "username": "Alice"}, b'aAlice'),
    ({"task": "login-username-reply", "user_exists": True, "username": "Alice"}, b'bTAlice'),
    ({"task": "send-message", "sender": "user1", "receiver": "user2", "sender_username": "Alice",
      "receiver_username": "Bob", "text": "Hello", "timestamp": "2023-01-01T12:00:00"},
     b'guser12023-01-01T12:00:0005user2Hello'),
])
def test_json_to_wire_protocol(json_message, expected_wire):
    """
    Test that JSON messages are correctly encoded into wire protocol.
    """
    wire_message = json_to_wire_protocol(json_message)
    assert wire_message == expected_wire

@pytest.mark.parametrize("wire_message, expected_json", [
    (b'aAlice', {"task": "login-username", "username": "Alice"}),
    (b'bTAlice', {"task": "login-username-reply", "user_exists": True, "username": "Alice"}),
])
def test_wire_protocol_to_json(wire_message, expected_json):
    """
    Test that wire protocol messages are correctly decoded into JSON.
    """
    json_message = wire_protocol_to_json(wire_message)
    assert json_message == expected_json

# ---------------- TESTS FOR SOCKET COMMUNICATION ---------------- #

def test_send_request_json_protocol():
    """
    Test that send_request() sends a JSON message correctly.
    """
    mock_socket = Mock()
    json_message = {"task": "login-username", "username": "Alice"}

    send_request(mock_socket, json_message, use_wire_protocol=False)

    expected_data = json.dumps(json_message).encode("utf-8")
    mock_socket.sendall.assert_called_once_with(expected_data)

def test_send_request_wire_protocol():
    """
    Test that send_request() sends a wire protocol message correctly.
    """
    mock_socket = Mock()
    json_message = {"task": "login-username", "username": "Alice"}

    send_request(mock_socket, json_message, use_wire_protocol=True)

    expected_data = b'aAlice'  # Expected wire protocol output
    mock_socket.sendall.assert_called_once_with(expected_data)

def test_receive_response_json_protocol():
    """
    Test that receive_response() correctly decodes a JSON response.
    """
    mock_socket = Mock()
    mock_socket.recv.return_value = json.dumps({"task": "login-username-reply", "user_exists": True}).encode("utf-8")

    response = receive_response(mock_socket, use_wire_protocol=False)

    assert response == {"task": "login-username-reply", "user_exists": True}

def test_receive_response_wire_protocol():
    """
    Test that receive_response() correctly decodes a wire protocol response.
    """
    mock_socket = Mock()
    mock_socket.recv.return_value = b'bTAlice'

    response = receive_response(mock_socket, use_wire_protocol=True)

    assert response == {'task': 'login-username-reply', 'user_exists': True, 'username': 'Alice'}

# ---------------- TESTS FOR PASSWORD HASHING ---------------- #

@pytest.mark.parametrize("password", ["password123", "securePass!", "admin"])
def test_hash_password(password):
    """
    Test if hash_password() correctly hashes passwords using SHA-256.
    """
    hashed_value = hash_password(password)
    expected_value = hashlib.sha256(password.encode()).hexdigest()

    assert hashed_value == expected_value
    assert len(hashed_value) == 64  # SHA-256 produces 64-character hex strings
