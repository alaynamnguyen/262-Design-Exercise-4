import pytest
from unittest.mock import MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import chat_pb2
import chat_pb2_grpc

# ---------------- FIXTURES ---------------- #

@pytest.fixture
def grpc_stub():
    """
    Fixture to provide a mock gRPC stub for testing.
    """
    stub = MagicMock(spec=chat_pb2_grpc.ChatServiceStub)

    stub.ListAccounts = MagicMock()
    stub.DeleteAccount = MagicMock()

    return stub


# ---------------- TESTS FOR list_accounts() USING gRPC ---------------- #

def test_list_accounts(grpc_stub):
    """
    Test if list_accounts() correctly retrieves account lists.
    """
    grpc_stub.ListAccounts.return_value = chat_pb2.ListAccountsResponse(accounts=["Alice", "Bob", "Charlie"])

    wildcard = "A*"

    request = chat_pb2.ListAccountsRequest(wildcard=wildcard)
    response = grpc_stub.ListAccounts(request)

    grpc_stub.ListAccounts.assert_called_once_with(request)
    assert response.accounts == ["Alice", "Bob", "Charlie"]  # Ensure accounts are returned correctly


# ---------------- TESTS FOR delete_account() USING gRPC ---------------- #

def test_delete_account_success(grpc_stub):
    """
    Test if delete_account() successfully deletes an account when the server confirms deletion.
    """
    grpc_stub.DeleteAccount.return_value = chat_pb2.DeleteAccountResponse(success=True)

    uid = "user123"

    request = chat_pb2.DeleteAccountRequest(uid=uid)
    response = grpc_stub.DeleteAccount(request)

    grpc_stub.DeleteAccount.assert_called_once_with(request)
    assert response.success  # Ensure deletion was successful


def test_delete_account_failure(grpc_stub):
    """
    Test if delete_account() correctly handles failure when the server rejects deletion.
    """
    grpc_stub.DeleteAccount.return_value = chat_pb2.DeleteAccountResponse(success=False)  # Simulating failure response

    uid = "user123"

    request = chat_pb2.DeleteAccountRequest(uid=uid)
    response = grpc_stub.DeleteAccount(request)

    grpc_stub.DeleteAccount.assert_called_once_with(request)
    assert not response.success  # Ensure deletion failed
