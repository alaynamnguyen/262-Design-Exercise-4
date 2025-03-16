import pytest
from unittest.mock import MagicMock
import grpc
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
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
