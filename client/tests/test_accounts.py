import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from controller.accounts import list_accounts, delete_account

# ---------------- TESTS FOR list_accounts() ---------------- #

@patch("controller.accounts.build_and_send_task")
def test_list_accounts(mock_build_and_send):
    """
    Test if list_accounts() correctly retrieves account lists.
    """
    mock_socket = Mock()
    mock_build_and_send.return_value = {"accounts": ["Alice", "Bob", "Charlie"]}

    wildcard = "A*"
    
    response = list_accounts(mock_socket, wildcard, use_wire_protocol=False)

    mock_build_and_send.assert_called_once_with(mock_socket, "list-accounts", False, wildcard=wildcard)
    assert response is None  # No return value, but should print results

# ---------------- TESTS FOR delete_account() ---------------- #

@patch("controller.accounts.build_and_send_task")
def test_delete_account_success(mock_build_and_send):
    """
    Test if delete_account() successfully deletes an account when the server confirms deletion.
    """
    mock_socket = Mock()
    mock_build_and_send.return_value = {"success": True}

    uid = "user123"

    response = delete_account(mock_socket, uid, use_wire_protocol=False)

    mock_build_and_send.assert_called_once_with(mock_socket, "delete-account", False, uid=uid)
    assert response == {"success": True}

@patch("controller.accounts.build_and_send_task")
def test_delete_account_failure(mock_build_and_send):
    """
    Test if delete_account() correctly handles failure when the server rejects deletion.
    """
    mock_socket = Mock()
    mock_build_and_send.return_value = {"success": False}  # Simulating failure response

    uid = "user123"

    response = delete_account(mock_socket, uid, use_wire_protocol=False)

    mock_build_and_send.assert_called_once_with(mock_socket, "delete-account", False, uid=uid)
    assert response == {"success": False}
