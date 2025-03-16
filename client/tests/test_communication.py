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

    stub.DeleteMessages = MagicMock()
    stub.MarkMessageRead = MagicMock()
    stub.SendMessage = MagicMock()
    stub.ListAccounts = MagicMock()
    stub.DeleteAccount = MagicMock()
    stub.GetReceivedMessages = MagicMock()
    stub.GetSentMessages = MagicMock()
    stub.GetMessageByMid = MagicMock()

    return stub


# ---------------- TESTS FOR delete_messages() USING gRPC ---------------- #

def test_delete_messages_success(grpc_stub):
    """
    Test if delete_messages() successfully deletes messages when the server confirms deletion.
    """
    grpc_stub.DeleteMessages.return_value = chat_pb2.DeleteMessagesResponse(success=True)

    mids = ["msg1", "msg2"]
    client_uid = "user123"

    request = chat_pb2.DeleteMessagesRequest(uid=client_uid, mids=mids)
    response = grpc_stub.DeleteMessages(request)

    grpc_stub.DeleteMessages.assert_called_once_with(request)
    assert response.success  # Ensure the server confirms deletion


def test_delete_messages_failure(grpc_stub):
    """
    Test if delete_messages() correctly handles failure when the server cannot delete messages.
    """
    grpc_stub.DeleteMessages.return_value = chat_pb2.DeleteMessagesResponse(success=False)

    mids = ["msg1", "msg2"]
    client_uid = "user123"

    request = chat_pb2.DeleteMessagesRequest(uid=client_uid, mids=mids)
    response = grpc_stub.DeleteMessages(request)

    grpc_stub.DeleteMessages.assert_called_once_with(request)
    assert not response.success  # Ensure the server reports failure


# ---------------- TESTS FOR mark_message_read() USING gRPC ---------------- #

def test_mark_message_read_success(grpc_stub):
    """
    Test if mark_message_read() successfully marks a message as read.
    """
    grpc_stub.MarkMessageRead.return_value = chat_pb2.MarkMessageReadResponse(success=True)

    mid = "msg1"

    request = chat_pb2.MarkMessageReadRequest(mid=mid)
    response = grpc_stub.MarkMessageRead(request)

    grpc_stub.MarkMessageRead.assert_called_once_with(request)
    assert response.success  # Ensure the server confirms marking as read


def test_mark_message_read_failure(grpc_stub):
    """
    Test if mark_message_read() correctly handles failure when the server cannot mark a message as read.
    """
    grpc_stub.MarkMessageRead.return_value = chat_pb2.MarkMessageReadResponse(success=False)

    mid = "msg1"

    request = chat_pb2.MarkMessageReadRequest(mid=mid)
    response = grpc_stub.MarkMessageRead(request)

    grpc_stub.MarkMessageRead.assert_called_once_with(request)
    assert not response.success  # Ensure the server reports failure


# ---------------- TESTS FOR send_message() USING gRPC ---------------- #

def test_send_message_success(grpc_stub):
    """
    Test if send_message() correctly sends a message and receives confirmation.
    """
    grpc_stub.SendMessage.return_value = chat_pb2.SendMessageResponse(success=True)

    request = chat_pb2.SendMessageRequest(sender="alice", receiver_username="bob", text="Hello", timestamp="2025-02-24 14:00:00")
    response = grpc_stub.SendMessage(request)

    grpc_stub.SendMessage.assert_called_once_with(request)
    assert response.success  # Ensure the message was sent successfully


def test_send_message_failure(grpc_stub):
    """
    Test if send_message() correctly handles failure when the server rejects the message.
    """
    grpc_stub.SendMessage.return_value = chat_pb2.SendMessageResponse(success=False)

    request = chat_pb2.SendMessageRequest(sender="alice", receiver_username="bob", text="Hello", timestamp="2025-02-24 14:00:00")
    response = grpc_stub.SendMessage(request)

    grpc_stub.SendMessage.assert_called_once_with(request)
    assert not response.success  # Ensure the server reports failure


# ---------------- TESTS FOR list_accounts() USING gRPC ---------------- #

def test_list_accounts(grpc_stub):
    """
    Test if list_accounts() correctly retrieves a list of matching accounts.
    """
    grpc_stub.ListAccounts.return_value = chat_pb2.ListAccountsResponse(accounts=["Alice", "Bob"])

    request = chat_pb2.ListAccountsRequest(wildcard="A*")
    response = grpc_stub.ListAccounts(request)

    grpc_stub.ListAccounts.assert_called_once_with(request)
    assert response.accounts == ["Alice", "Bob"]  # Ensure correct accounts are returned


# ---------------- TESTS FOR delete_account() USING gRPC ---------------- #

def test_delete_account_success(grpc_stub):
    """
    Test if delete_account() successfully deletes a user account.
    """
    grpc_stub.DeleteAccount.return_value = chat_pb2.DeleteAccountResponse(success=True)

    request = chat_pb2.DeleteAccountRequest(uid="user123")
    response = grpc_stub.DeleteAccount(request)

    grpc_stub.DeleteAccount.assert_called_once_with(request)
    assert response.success  # Ensure account was deleted


def test_delete_account_failure(grpc_stub):
    """
    Test if delete_account() correctly handles failure when the server rejects account deletion.
    """
    grpc_stub.DeleteAccount.return_value = chat_pb2.DeleteAccountResponse(success=False)

    request = chat_pb2.DeleteAccountRequest(uid="user123")
    response = grpc_stub.DeleteAccount(request)

    grpc_stub.DeleteAccount.assert_called_once_with(request)
    assert not response.success  # Ensure deletion failed


# ---------------- TESTS FOR get_messages() USING gRPC ---------------- #

def test_get_received_messages(grpc_stub):
    """
    Test if get_messages() retrieves received messages correctly.
    """
    grpc_stub.GetReceivedMessages.return_value = chat_pb2.GetMessagesResponse(mids=["msg1", "msg2"])

    request = chat_pb2.GetMessagesRequest(uid="alice_uid")
    response = grpc_stub.GetReceivedMessages(request)

    grpc_stub.GetReceivedMessages.assert_called_once_with(request)
    assert response.mids == ["msg1", "msg2"]  # Ensure correct messages are returned


def test_get_sent_messages(grpc_stub):
    """
    Test if get_messages() retrieves sent messages correctly.
    """
    grpc_stub.GetSentMessages.return_value = chat_pb2.GetMessagesResponse(mids=["msg3", "msg4"])

    request = chat_pb2.GetMessagesRequest(uid="alice_uid")
    response = grpc_stub.GetSentMessages(request)

    grpc_stub.GetSentMessages.assert_called_once_with(request)
    assert response.mids == ["msg3", "msg4"]  # Ensure correct messages are returned


# ---------------- TESTS FOR get_message_by_mid() USING gRPC ---------------- #

def test_get_message_by_mid(grpc_stub):
    """
    Test if get_message_by_mid() correctly retrieves a message's details.
    """
    grpc_stub.GetMessageByMid.return_value = chat_pb2.GetMessageResponse(
        sender_uid="alice_uid",
        receiver_uid="bob_uid",
        sender_username="Alice",
        receiver_username="Bob",
        text="Hello, Bob!",
        timestamp="2025-02-24 14:00:00",
        receiver_read=True
    )

    request = chat_pb2.GetMessageRequest(mid="msg1")
    response = grpc_stub.GetMessageByMid(request)

    grpc_stub.GetMessageByMid.assert_called_once_with(request)
    assert response.sender_username == "Alice"
    assert response.receiver_username == "Bob"
    assert response.text == "Hello, Bob!"
    assert response.receiver_read is True
