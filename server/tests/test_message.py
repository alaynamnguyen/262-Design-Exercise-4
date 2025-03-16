import pytest
import os
import sys
import uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from datetime import datetime
from model.message import Message

# ----------------- FIXTURES ----------------- #

@pytest.fixture
def sample_message():
    """
    Fixture to create a sample message instance for tests.
    """
    return Message(
        sender="user1",
        receiver="user2",
        sender_username="Alice",
        receiver_username="Bob",
        text="Hello, Bob!"
    )

@pytest.fixture
def custom_message():
    """
    Fixture to create a message with custom values.
    """
    return Message(
        sender="user1",
        receiver="user3",
        sender_username="Alice",
        receiver_username="Charlie",
        text="Custom message",
        mid="custom_mid_123",
        timestamp="2023-01-01T12:00:00",
        receiver_read=True
    )

# ----------------- INIT TESTS ----------------- #

def test_message_default_values():
    """
    Test default values for optional parameters.
    """
    message = Message(
        sender="user1",
        receiver="user2",
        sender_username="Alice",
        receiver_username="Bob",
        text="Default test"
    )

    assert isinstance(message.mid, str)  # Should be a UUID string
    assert isinstance(message.timestamp, str)  # Should be stored as a string
    assert datetime.fromisoformat(message.timestamp) <= datetime.now()  # Should be recent
    assert message.receiver_read is False  # Default should be False

def test_message_custom_values(custom_message):
    """
    Test that all custom values are correctly assigned.
    """
    assert custom_message.sender == "user1"
    assert custom_message.receiver == "user3"
    assert custom_message.sender_username == "Alice"
    assert custom_message.receiver_username == "Charlie"
    assert custom_message.text == "Custom message"
    assert custom_message.mid == "custom_mid_123"
    assert custom_message.timestamp == "2023-01-01T12:00:00"
    assert custom_message.receiver_read is True  # Custom value

# ----------------- FUNCTION TESTS ----------------- #

def test_message_mark_as_read(sample_message):
    """
    Test that mark_as_read() method updates receiver_read.
    """
    assert not sample_message.receiver_read  # Initially False

    sample_message.mark_as_read()

    assert sample_message.receiver_read  # Should be True after marking as read

def test_message_repr(sample_message):
    """
    Test the __repr__ method of the Message class.
    """
    repr_str = repr(sample_message)

    assert "Message(mid=" in repr_str
    assert f"sender={sample_message.sender}" in repr_str
    assert f"receiver={sample_message.receiver}" in repr_str
    assert f"text={sample_message.text}" in repr_str

# ----------------- EDGE CASE TESTS ----------------- #

def test_message_empty_text():
    """
    Test that an empty message text is allowed.
    """
    message = Message(
        sender="user1",
        receiver="user2",
        sender_username="Alice",
        receiver_username="Bob",
        text=""
    )

    assert message.text == ""  # Should allow empty text

def test_message_long_text():
    """
    Test handling of long message text.
    """
    long_text = "A" * 5000  # 5000-character long text
    message = Message(
        sender="user1",
        receiver="user2",
        sender_username="Alice",
        receiver_username="Bob",
        text=long_text
    )

    assert message.text == long_text  # Should store the long text correctly

def test_message_unique_id():
    """
    Test that each message gets a unique ID.
    """
    message1 = Message(
        sender="user1",
        receiver="user2",
        sender_username="Alice",
        receiver_username="Bob",
        text="First message!"
    )

    message2 = Message(
        sender="user1",
        receiver="user3",
        sender_username="Alice",
        receiver_username="Charlie",
        text="Second message!"
    )

    assert message1.mid != message2.mid  # Each message should have a unique ID

def test_message_timestamp_format(sample_message):
    """
    Test that the timestamp is stored in ISO 8601 format.
    """
    try:
        datetime.fromisoformat(sample_message.timestamp)  # Should not raise an error
        assert True
    except ValueError:
        pytest.fail("Timestamp is not in ISO 8601 format")
