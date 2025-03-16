import pytest
import uuid
from model.user import User

def test_create_user():
    """
    Test the creation of a User object with a username and password.
    """
    user = User(username="testuser", password="secure123")
    
    assert user.username == "testuser"
    assert user.password == "secure123"
    assert user.active is True
    assert isinstance(user.uid, str)
    assert isinstance(user.received_messages, list)
    assert isinstance(user.sent_messages, list)
    assert len(user.received_messages) == 0
    assert len(user.sent_messages) == 0

def test_create_user_with_custom_uid():
    """
    Test creating a User object with a specific UID.
    """
    custom_uid = str(uuid.uuid4())
    user = User(username="customuser", password="mypassword", uid=custom_uid)
    
    assert user.uid == custom_uid

def test_create_inactive_user():
    """
    Test creating a User object that is inactive.
    """
    user = User(username="inactiveuser", password="password", active=False)
    
    assert user.active is False

def test_add_sent_message():
    """
    Test adding a sent message ID to the user's sent_messages list.
    """
    user = User(username="sender", password="pass")
    user.sent_messages.append("msg1")

    assert len(user.sent_messages) == 1
    assert "msg1" in user.sent_messages

def test_add_received_message():
    """
    Test adding a received message ID to the user's received_messages list.
    """
    user = User(username="receiver", password="pass")
    user.received_messages.append("msg2")

    assert len(user.received_messages) == 1
    assert "msg2" in user.received_messages

def test_user_repr():
    """
    Test the __repr__ method of the User class.
    """
    user = User(username="testuser", password="secure123")
    repr_str = repr(user)

    assert "User(uid=" in repr_str
    assert "username=testuser" in repr_str
    assert "password=secure123" in repr_str
    assert "received_messages=" in repr_str
    assert "sent_messages=" in repr_str
    assert "active=True" in repr_str
