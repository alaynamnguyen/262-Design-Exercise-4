import pytest
import os
import sys
import uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import (
    json_to_wire_protocol, wire_protocol_to_json,
    object_to_dict_recursive, dict_to_object_recursive
)
from model.user import User
from model.message import Message

# ------------------ JSON <-> WIRE PROTOCOL TESTS ------------------ #

@pytest.mark.parametrize("json_message, expected_wire", [
    ({"task": "login-username", "username": "Alice"}, "aAlice"),
    ({"task": "login-username-reply", "user_exists": True, "username": "Alice"}, "bTAlice"),
    ({"task": "send-message", "sender": "user1", "receiver": "user2", "sender_username": "Alice",
      "receiver_username": "Bob", "text": "Hello", "timestamp": "2023-01-01T12:00:00"},
     "guser12023-01-01T12:00:0005user2Hello"),
])
def test_json_to_wire_protocol(json_message, expected_wire):
    """
    Test that JSON messages are correctly encoded into wire protocol.
    """
    wire_message = json_to_wire_protocol(json_message).decode("utf-8")
    assert wire_message == expected_wire

@pytest.mark.parametrize("wire_message, expected_json", [
    ("aAlice", {"task": "login-username", "username": "Alice"}),
    ("bTAlice", {"task": "login-username-reply", "user_exists": True, "username": "Alice"}),
])
def test_wire_protocol_to_json(wire_message, expected_json):
    """
    Test that wire protocol messages are correctly decoded into JSON.
    """
    json_message = wire_protocol_to_json(wire_message)
    assert json_message == expected_json

# ------------------ OBJECT <-> DICTIONARY TESTS ------------------ #

def test_object_to_dict_user():
    """
    Test that a User object is correctly converted to a dictionary.
    """
    user = User(username="Alice", password="secure123", uid="123")
    user_dict = object_to_dict_recursive(user)

    assert isinstance(user_dict, dict)
    assert user_dict["uid"] == "123"
    assert user_dict["username"] == "Alice"
    assert user_dict["password"] == "secure123"
    assert user_dict["active"] is True
    assert "sent_messages" in user_dict
    assert "received_messages" in user_dict

def test_dict_to_object_user():
    """
    Test that a dictionary is correctly converted back to a User object.
    """
    user_dict = {
        "uid": "123",
        "username": "Alice",
        "password": "secure123",
        "active": True,
        "sent_messages": [],
        "received_messages": []
    }
    
    user = dict_to_object_recursive(user_dict, User)

    assert isinstance(user, User)
    assert user.uid == "123"
    assert user.username == "Alice"
    assert user.password == "secure123"
    assert user.active is True
    assert user.sent_messages == []
    assert user.received_messages == []

def test_object_to_dict_message():
    """
    Test that a Message object is correctly converted to a dictionary.
    """
    message = Message(
        sender="user1",
        receiver="user2",
        sender_username="Alice",
        receiver_username="Bob",
        text="Hello",
        mid="msg123",
        timestamp="2023-01-01T12:00:00"
    )

    message_dict = object_to_dict_recursive(message)

    assert isinstance(message_dict, dict)
    assert message_dict["sender"] == "user1"
    assert message_dict["receiver"] == "user2"
    assert message_dict["sender_username"] == "Alice"
    assert message_dict["receiver_username"] == "Bob"
    assert message_dict["text"] == "Hello"
    assert message_dict["mid"] == "msg123"
    assert message_dict["timestamp"] == "2023-01-01T12:00:00"
    assert message_dict["receiver_read"] is False

def test_dict_to_object_message():
    """
    Test that a dictionary is correctly converted back to a Message object.
    """
    message_dict = {
        "sender": "user1",
        "receiver": "user2",
        "sender_username": "Alice",
        "receiver_username": "Bob",
        "text": "Hello",
        "mid": "msg123",
        "timestamp": "2023-01-01T12:00:00",
        "receiver_read": False
    }

    message = dict_to_object_recursive(message_dict, Message)

    assert isinstance(message, Message)
    assert message.sender == "user1"
    assert message.receiver == "user2"
    assert message.sender_username == "Alice"
    assert message.receiver_username == "Bob"
    assert message.text == "Hello"
    assert message.mid == "msg123"
    assert message.timestamp == "2023-01-01T12:00:00"
    assert message.receiver_read is False
