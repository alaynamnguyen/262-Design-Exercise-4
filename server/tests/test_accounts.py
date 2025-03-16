import pytest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from model.user import User

from controller.accounts import list_accounts, delete_account
from model.user import User

# ---------------- FIXTURES ---------------- #

@pytest.fixture
def sample_users():
    """
    Fixture to provide a sample dictionary of users.
    """
    return {
        "user1": User(username="Alice", password="secure123", uid="user1", active=True),
        "user2": User(username="Bob", password="pass123", uid="user2", active=True),
        "user3": User(username="Charlie", password="qwerty", uid="user3", active=False),  # Inactive user
        "user4": User(username="David", password="abcd", uid="user4", active=True)
    }

# ---------------- TESTS FOR list_accounts() ---------------- #

def test_list_accounts_all_active(sample_users):
    """
    Test if list_accounts() returns all active accounts.
    """
    active_accounts = list_accounts(sample_users)
    
    assert sorted(active_accounts) == sorted(["Alice", "Bob", "David"])

def test_list_accounts_with_wildcard(sample_users):
    """
    Test if list_accounts() correctly filters active accounts using a wildcard.
    """
    filtered_accounts = list_accounts(sample_users, wildcard="A*")

    assert filtered_accounts == ["Alice"]  # Only Alice matches "A*"

def test_list_accounts_no_match(sample_users):
    """
    Test if list_accounts() returns an empty list when no accounts match the wildcard.
    """
    filtered_accounts = list_accounts(sample_users, wildcard="Z*")

    assert filtered_accounts == []  # No users match "Z*"

# ---------------- TESTS FOR delete_account() ---------------- #

def test_delete_account_success(sample_users):
    """
    Test if delete_account() successfully marks an account as inactive.
    """
    assert sample_users["user1"].active is True

    result = delete_account(sample_users, "user1")

    assert result is True
    assert sample_users["user1"].active is False  # Should now be inactive

def test_delete_account_already_inactive(sample_users):
    """
    Test if delete_account() correctly processes an already inactive user.
    """
    assert sample_users["user3"].active is False  # Charlie is already inactive

    result = delete_account(sample_users, "user3")

    assert result is True  # Still returns True even if already inactive
    assert sample_users["user3"].active is False  # Should remain inactive

def test_delete_account_invalid_uid(sample_users):
    """
    Test if delete_account() raises a KeyError for a non-existent user.
    """
    with pytest.raises(KeyError):
        delete_account(sample_users, "nonexistent_user")
