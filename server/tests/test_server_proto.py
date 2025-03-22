import pytest
import grpc
import sys
import os
from concurrent import futures
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import server_proto
import chat_pb2
import chat_pb2_grpc

# ---------- FIXTURES ---------- #

@pytest.fixture(scope="module")
def grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))

    chat_service = server_proto.ChatService(
        is_leader=True,
        local_ip="127.0.0.1",
        local_port="50051",
        leader_ip="127.0.0.1",
        leader_port="50051",
        heartbeat_interval=1
    )
    chat_service.replica_list = ["127.0.0.1:50051"]  # Manually set for tests

    chat_pb2_grpc.add_ChatServiceServicer_to_server(chat_service, server)
    server.add_insecure_port("127.0.0.1:50051")
    server.start()
    time.sleep(1)

    yield server
    server.stop(None)

@pytest.fixture(scope="module")
def grpc_channel(grpc_server):
    channel = grpc.insecure_channel("127.0.0.1:50051")
    yield channel
    channel.close()

@pytest.fixture
def grpc_stub(grpc_channel):
    return chat_pb2_grpc.ChatServiceStub(grpc_channel)

# ---------- TESTS ---------- #

def test_delete_account(grpc_stub):
    username = "delete_me"
    password = "delete123"

    create = grpc_stub.LoginPassword(chat_pb2.LoginPasswordRequest(username=username, password=password))
    assert create.success
    uid = create.uid

    response = grpc_stub.DeleteAccount(chat_pb2.DeleteAccountRequest(uid=uid))
    assert response.success

def test_send_and_retrieve_message(grpc_stub):
    sender = "alice"
    receiver = "bob"
    pw = "pw"

    sender_uid = grpc_stub.LoginPassword(chat_pb2.LoginPasswordRequest(username=sender, password=pw)).uid
    receiver_uid = grpc_stub.LoginPassword(chat_pb2.LoginPasswordRequest(username=receiver, password=pw)).uid

    send = grpc_stub.SendMessage(chat_pb2.SendMessageRequest(
        sender=sender_uid,
        receiver_username=receiver,
        text="Hi Bob!",
        timestamp="2025-01-01 10:00:00"
    ))
    assert send.success

    sent = grpc_stub.GetSentMessages(chat_pb2.GetMessagesRequest(uid=sender_uid))
    received = grpc_stub.GetReceivedMessages(chat_pb2.GetMessagesRequest(uid=receiver_uid))

    assert sent.mids
    assert received.mids

    mid = sent.mids[0]
    message = grpc_stub.GetMessageByMid(chat_pb2.GetMessageRequest(mid=mid))
    assert message.text == "Hi Bob!"
    assert message.receiver_username == receiver

def test_mark_message_read(grpc_stub):
    sender = "charlie"
    receiver = "dave"
    pw = "pw"

    sender_uid = grpc_stub.LoginPassword(chat_pb2.LoginPasswordRequest(username=sender, password=pw)).uid
    receiver_uid = grpc_stub.LoginPassword(chat_pb2.LoginPasswordRequest(username=receiver, password=pw)).uid

    send = grpc_stub.SendMessage(chat_pb2.SendMessageRequest(
        sender=sender_uid,
        receiver_username=receiver,
        text="Read this!",
        timestamp="2025-01-01 11:00:00"
    ))
    assert send.success

    received = grpc_stub.GetReceivedMessages(chat_pb2.GetMessagesRequest(uid=receiver_uid))
    mid = received.mids[0]

    mark = grpc_stub.MarkMessageRead(chat_pb2.MarkMessageReadRequest(mid=mid))
    assert mark.success

def test_delete_message(grpc_stub):
    sender = "eve"
    receiver = "frank"
    pw = "pw"

    sender_uid = grpc_stub.LoginPassword(chat_pb2.LoginPasswordRequest(username=sender, password=pw)).uid
    receiver_uid = grpc_stub.LoginPassword(chat_pb2.LoginPasswordRequest(username=receiver, password=pw)).uid

    send = grpc_stub.SendMessage(chat_pb2.SendMessageRequest(
        sender=sender_uid,
        receiver_username=receiver,
        text="Temporary message",
        timestamp="2025-01-01 12:00:00"
    ))
    assert send.success

    sent = grpc_stub.GetSentMessages(chat_pb2.GetMessagesRequest(uid=sender_uid))
    mid = sent.mids[0]

    delete = grpc_stub.DeleteMessages(chat_pb2.DeleteMessagesRequest(uid=sender_uid, mids=[mid]))
    assert delete.success

def test_get_replica_list(grpc_stub):
    response = grpc_stub.GetReplicaList(chat_pb2.Empty())
    assert response.leader_address == "127.0.0.1:50051"
    assert "127.0.0.1:50051" in response.replica_list

def test_heartbeat_response(grpc_stub):
    """
    Test that the server responds to heartbeat pings.
    """
    request = chat_pb2.HeartbeatRequest(server_id="test_replica:50052")
    response = grpc_stub.Heartbeat(request)
    assert response.success

def test_replica_list_contains_leader(grpc_stub):
    """
    Verify that the leader's address is always included in the replica list.
    """
    response = grpc_stub.GetReplicaList(chat_pb2.Empty())
    assert response.leader_address in response.replica_list

def test_leader_election_logic():
    """
    Unit test the logic of electing the new leader.
    """
    chat_service = server_proto.ChatService(
        is_leader=False,
        local_ip="127.0.0.3",
        local_port="60001",
        leader_ip="127.0.0.1",
        leader_port="60000",
        heartbeat_interval=1
    )
    chat_service.local_address = "127.0.0.3:60001"
    chat_service.replica_list = [
        "127.0.0.1:60000",  # Old leader
        "127.0.0.2:60002",
        "127.0.0.3:60001"   # Current server
    ]
    chat_service.leader_address = "127.0.0.1:60000"

    chat_service.leader_election()

    # Check new leader is lowest lexicographically
    assert chat_service.leader_address == "127.0.0.2:60002"
    assert not chat_service.is_leader  # This server is not the new leader

def test_sync_users_from_leader(grpc_stub):
    """
    Test syncing user data from the leader to a replica.
    """
    test_user = chat_pb2.UserData(
        uid="sync-user-uid",
        username="sync_user",
        password="fakehash",
        received_messages=[],
        sent_messages=[],
        active=True
    )
    request = chat_pb2.UserSyncRequest(users=[test_user])
    response = grpc_stub.SyncUsersFromLeader(request)
    assert response.success

    # Confirm the user exists via login
    username_request = chat_pb2.LoginUsernameRequest(username="sync_user")
    check = grpc_stub.LoginUsername(username_request)
    assert check.user_exists

def test_sync_messages_from_leader(grpc_stub):
    """
    Test syncing messages from the leader to a replica.
    """
    test_message = chat_pb2.MessageData(
        sender="sync-user-uid",
        receiver="sync-receiver-uid",
        sender_username="sync_user",
        receiver_username="sync_receiver",
        text="Synced message!",
        mid="sync-mid-001",
        timestamp="2025-03-23 14:00:00",
        receiver_read=False
    )
    request = chat_pb2.MessageSyncRequest(messages=[test_message])
    response = grpc_stub.SyncMessagesFromLeader(request)
    assert response.success

    # Confirm the message is now retrievable
    message = grpc_stub.GetMessageByMid(chat_pb2.GetMessageRequest(mid="sync-mid-001"))
    assert message.text == "Synced message!"
    assert message.sender_username == "sync_user"

def test_sync_replica_list_from_leader(grpc_stub):
    """
    Test syncing replica list from the leader to a replica.
    """
    test_list = [
        "127.0.0.1:50051",
        "127.0.0.2:60000",
        "127.0.0.3:60001"
    ]
    request = chat_pb2.ReplicaListSyncRequest(replica_list=test_list)
    response = grpc_stub.SyncReplicaListFromLeader(request)
    assert response.success

    # Confirm via GetReplicaList that the list matches
    replica_info = grpc_stub.GetReplicaList(chat_pb2.Empty())
    assert sorted(replica_info.replica_list) == sorted(test_list)
