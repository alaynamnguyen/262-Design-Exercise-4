import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from controller.client_messages import (
    delete_messages, mark_message_read
)

# ---------------- TESTS FOR delete_messages() ---------------- #

@patch("controller.client_messages.build_and_send_task")
def test_delete_messages_success(mock_build_and_send):
    """
    Test if delete_messages() successfully deletes messages when the server confirms deletion.
    """
    mock_socket = Mock()
    mock_build_and_send.return_value = {"success": True}

    mids = ["msg1", "msg2"]
    client_uid = "user123"
    
    response = delete_messages(mock_socket, mids, client_uid, use_wire_protocol=False)

    mock_build_and_send.assert_called_once_with(mock_socket, "delete-messages", False, mids=mids, uid=client_uid)
    assert response is None  # No return value, but should print success message

@patch("controller.client_messages.build_and_send_task")
def test_delete_messages_failure(mock_build_and_send):
    """
    Test if delete_messages() correctly handles failure when the server cannot delete messages.
    """
    mock_socket = Mock()
    mock_build_and_send.return_value = {"success": False}

    mids = ["msg1", "msg2"]
    client_uid = "user123"
    
    response = delete_messages(mock_socket, mids, client_uid, use_wire_protocol=False)

    mock_build_and_send.assert_called_once_with(mock_socket, "delete-messages", False, mids=mids, uid=client_uid)
    assert response is None  # Should print failure message

# ---------------- TESTS FOR mark_message_read() ---------------- #

@patch("controller.client_messages.build_and_send_task")
def test_mark_message_read_success(mock_build_and_send):
    """
    Test if mark_message_read() successfully marks a message as read.
    """
    mock_socket = Mock()
    mock_build_and_send.return_value = {"success": True}

    mid = "msg1"

    response = mark_message_read(mock_socket, mid, use_wire_protocol=False)

    mock_build_and_send.assert_called_once_with(mock_socket, "mark-message-read", False, mid=mid)
    assert response is None  # No return value, but should print confirmation message

@patch("controller.client_messages.build_and_send_task")
def test_mark_message_read_failure(mock_build_and_send):
    """
    Test if mark_message_read() correctly handles failure when the server cannot mark a message as read.
    """
    mock_socket = Mock()
    mock_build_and_send.return_value = {"success": False}  # Simulating failure response

    mid = "msg1"

    response = mark_message_read(mock_socket, mid, use_wire_protocol=False)

    mock_build_and_send.assert_called_once_with(mock_socket, "mark-message-read", False, mid=mid)
    assert response is None  # Should print failure message
