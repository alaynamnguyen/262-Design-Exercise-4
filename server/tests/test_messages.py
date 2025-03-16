import pytest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from controller.messages import (
    send_message, delete_messages, mark_message_read,
    get_message_by_mid, get_sent_messages_id, get_received_messages_id
)
from model.user import User
from model.message import Message
from unittest.mock import Mock

# ---------------- FIXTURES ---------------- #

@pytest.fixture
def sample_users():
    """
    Fixture to provide a sample dictionary of users.
    """
    return {
        "user1": User(username="Alice", password="secure123", uid="user1"),
        "user2": User(username="Bob", password="pass123", uid="user2"),
        "user3": User(username="Charlie", password="qwerty", uid="user3", active=False)  # Inactive user
    }

@pytest.fixture
def sample_messages():
    """
    Fixture to provide a sample dictionary of messages.
    """
    return {
        "msg1": Message(sender="user1", receiver="user2", sender_username="Alice", receiver_username="Bob",
                        text="Hello, Bob!", mid="msg1", timestamp="2023-01-01T12:00:00"),
        "msg2": Message(sender="user2", receiver="user1", sender_username="Bob", receiver_username="Alice",
                        text="Hey Alice!", mid="msg2", timestamp="2023-01-02T12:00:00")
    }

@pytest.fixture
def connected_clients():
    """
    Fixture to simulate connected clients dictionary.
    """
    return {}

# ---------------- TESTS FOR MESSAGE SENDING ---------------- #

def test_send_message_success(sample_users, sample_messages, connected_clients):
    """
    Test if send_message() successfully sends a message.
    """
    timestamp = "2023-01-03T10:00:00"
    result = send_message(
        sender_uid="user1",
        receiver_username="Bob",
        text="Hey Bob!",
        users_dict=sample_users,
        messages_dict=sample_messages,
        timestamp=timestamp,
        connected_clients=connected_clients
    )

    assert result is True
    assert any(msg.text == "Hey Bob!" for msg in sample_messages.values())

def test_send_message_receiver_not_found(sample_users, sample_messages, connected_clients):
    """
    Test if send_message() fails when recipient does not exist.
    """
    timestamp = "2023-01-03T10:00:00"
    result = send_message(
        sender_uid="user1",
        receiver_username="NonExistentUser",
        text="Hello?",
        users_dict=sample_users,
        messages_dict=sample_messages,
        timestamp=timestamp,
        connected_clients=connected_clients
    )

    assert result is False

def test_send_message_receiver_inactive(sample_users, sample_messages, connected_clients):
    """
    Test if send_message() fails when recipient is inactive.
    """
    timestamp = "2023-01-03T10:00:00"
    result = send_message(
        sender_uid="user1",
        receiver_username="Charlie",
        text="Are you there?",
        users_dict=sample_users,
        messages_dict=sample_messages,
        timestamp=timestamp,
        connected_clients=connected_clients
    )

    assert result is False

# ---------------- TESTS FOR MESSAGE DELETION ---------------- #

def test_delete_messages_success(sample_users, sample_messages):
    """
    Test if delete_messages() successfully removes messages.
    """
    sample_users["user1"].sent_messages.append("msg1")
    sample_users["user2"].received_messages.append("msg1")

    success, deleted_mids = delete_messages(sample_users, sample_messages, ["msg1"], "user1")

    assert success is True
    assert "msg1" not in sample_users["user1"].sent_messages

def test_delete_messages_not_found(sample_users, sample_messages):
    """
    Test if delete_messages() fails when message is not found.
    """
    success, deleted_mids = delete_messages(sample_users, sample_messages, ["nonexistent_msg"], "user1")

    assert success is False
    assert deleted_mids == []

# ---------------- TESTS FOR MESSAGE MARKING ---------------- #

def test_mark_message_read_success(sample_messages):
    """
    Test if mark_message_read() correctly updates receiver_read.
    """
    assert sample_messages["msg1"].receiver_read is False

    result = mark_message_read(sample_messages, "msg1")

    assert result is True
    assert sample_messages["msg1"].receiver_read is True

def test_mark_message_read_not_found(sample_messages):
    """
    Test if mark_message_read() fails when message ID does not exist.
    """
    result = mark_message_read(sample_messages, "invalid_mid")

    assert result is False

# ---------------- TESTS FOR MESSAGE RETRIEVAL ---------------- #

def test_get_message_by_mid_success(sample_messages):
    """
    Test if get_message_by_mid() correctly retrieves a message as a dictionary.
    """
    msg_dict = get_message_by_mid("msg1", sample_messages)

    assert msg_dict is not None
    assert msg_dict["mid"] == "msg1"
    assert msg_dict["text"] == "Hello, Bob!"

def test_get_message_by_mid_not_found(sample_messages):
    """
    Test if get_message_by_mid() returns None when message is not found.
    """
    msg_dict = get_message_by_mid("nonexistent_msg", sample_messages)

    assert msg_dict is None

# ---------------- TESTS FOR MESSAGE ID RETRIEVAL ---------------- #

def test_get_sent_messages_id(sample_users):
    """
    Test if get_sent_messages_id() correctly retrieves sent message IDs.
    """
    sample_users["user1"].sent_messages = ["msg1", "msg2"]

    sent_mids = get_sent_messages_id("user1", sample_users)

    assert sent_mids == ["msg1", "msg2"]

def test_get_received_messages_id(sample_users):
    """
    Test if get_received_messages_id() correctly retrieves received message IDs.
    """
    sample_users["user2"].received_messages = ["msg1"]

    received_mids = get_received_messages_id("user2", sample_users)

    assert received_mids == ["msg1"]
