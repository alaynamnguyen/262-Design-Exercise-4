import argparse
import grpc
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import chat_pb2
import chat_pb2_grpc
from concurrent import futures
import json
import hashlib
import configparser
from controller.login import check_username_exists, check_username_password, create_account
from controller.accounts import list_accounts, delete_account
from controller.messages import get_message_by_mid, get_received_messages_id, get_sent_messages_id, send_message, mark_message_read, delete_messages
from model import User, Message
from utils import dict_to_object_recursive, object_to_dict_recursive, protobuf_list_to_object, object_to_protobuf_list
import socket
import threading
import time

# Load config
config = configparser.ConfigParser()
config.read("config.ini")

HOST = config["network"]["host"]

def load_users_and_messages(ip, port):
    """Loads user data from the JSON file."""

    print("Calling load_users_and_messages")
    # User dict
    users_dict = dict()
    user_filepath = f"server/data/user_{ip}_{port}.json"
    
    if os.path.exists(user_filepath):
        with open(user_filepath, "r") as f:
            users = json.load(f)
        for k, v in users.items():
            user = dict_to_object_recursive(v, User)
            users_dict[user.uid] = user
    
    # Message dict
    messages_dict = dict()
    message_filepath = f"server/data/message_{ip}_{port}.json"
    print(f"    User and message json files exist: ", os.path.exists(user_filepath), os.path.exists(message_filepath))

    if os.path.exists(message_filepath):
        with open(message_filepath, "r") as f:
            messages = json.load(f)
        for k, v in messages.items():
            message = dict_to_object_recursive(v, Message)
            messages_dict[message.mid] = message
    
    return users_dict, messages_dict


def save_users_and_messages(ip, port, users_dict, messages_dict):
    """Saves user data to the JSON file."""
    print("Calling save_users_and_messages")
    with open(f"server/data/user_{ip}_{port}.json", "w") as f:
        json.dump(users_dict, f, default=object_to_dict_recursive, indent=4)
    print(f"    Finished writing users_dict")

    with open(f"server/data/message_{ip}_{port}.json", "w") as f:
        json.dump(messages_dict, f, default=object_to_dict_recursive, indent=4)
    print(f"    Finished writing messages_dict")


def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


class ChatService(chat_pb2_grpc.ChatServiceServicer):
    
    def __init__(self, is_leader, local_ip, local_port, leader_ip, leader_port, heartbeat_interval):
        """Initializes the ChatService with user and message data."""
        self.is_leader = is_leader
        self.local_ip = local_ip
        self.local_port = local_port
        self.local_address = f"{self.local_ip}:{self.local_port}"
        self.leader_ip = leader_ip
        self.leader_port = leader_port
        self.leader_address = f"{self.leader_ip}:{self.leader_port}"
        self.users_dict, self.messages_dict = load_users_and_messages(self.local_ip, self.local_port)  # Load users and messages from process specific persistent storage
        self.heartbeat_interval = heartbeat_interval

    def start_heartbeat_loop(self):
        """Start sending heartbeat pings to the leader on a background thread."""
        def heartbeat_loop():
            while True:
                try:
                    with grpc.insecure_channel(self.leader_address) as channel:
                        stub = chat_pb2_grpc.ChatServiceStub(channel)
                        print(f"Sending heartbeat request to leader {self.leader_address}")
                        request = chat_pb2.HeartbeatRequest(server_id=self.local_address)
                        response = stub.Heartbeat(request)
                        assert(response.success)
                except Exception as e:
                    print(f"Heartbeat failed: {e}")
                    self.leader_election()
                    print(f"Im leader: {self.is_leader}")
                    if self.is_leader: break

                time.sleep(self.heartbeat_interval)

        threading.Thread(target=heartbeat_loop, daemon=True).start()

    def start_leader_heartbeat_loop(self):
        def leader_heartbeat_loop():
            replica_down = False
            while True:
                for replica in self.replica_list:
                    try:
                        with grpc.insecure_channel(replica) as channel:
                            stub = chat_pb2_grpc.ChatServiceStub(channel)
                            print(f"Sending heartbeat request to replica {replica}")
                            request = chat_pb2.HeartbeatRequest(server_id=self.leader_address)
                            response = stub.Heartbeat(request)
                            assert(response.success)
                    except Exception as e:
                        replica_down = True
                        self.replica_list.remove(replica)
                        print(f"Replica down {replica}, removed from replica_list")
                
                # If replica list changed, propogate updated list to all other replicas
                if replica_down:
                    for replica in self.replica_list:
                        self.push_replica_list_to_replica(replica)

                time.sleep(self.heartbeat_interval)

        threading.Thread(target=leader_heartbeat_loop, daemon=True).start()

    def leader_election(self):
        print("Calling Leader Election")
        # Remove old leader from replica_list
        print("    Old replica list:", self.replica_list)
        self.replica_list.remove(self.leader_address)
        self.start_leader_heartbeat_loop()
        print(f"    Removed leader replica list {self.replica_list}")

        # Elect new leader (min ip/port combo from replica list)
        new_leader_address = min(self.replica_list)
        
        if self.local_address == new_leader_address:
            self.is_leader = True
            # Now update the config with your local address

        # Update everyone's params to new leade
        self.leader_ip, self.leader_port = new_leader_address.split(":")
        self.leader_address = f"{self.leader_ip}:{self.leader_port}"
        print("    New leader elected:", self.leader_address)

    def on_server_start(self):
        """Setup server when server starts"""
        print("Calling on_server_start")
        if self.is_leader:  # Leader server initialization
            self.replica_list = [args.leader_address] # Leader is included in the replica_list
            self.start_leader_heartbeat_loop()
        else:  # Replica server initialization
            with grpc.insecure_channel(f"{self.leader_ip}:{self.leader_port}") as channel:
                stub = chat_pb2_grpc.ChatServiceStub(channel)
                request = chat_pb2.RegisterReplicaRequest(ip_address=self.local_ip, port=self.local_port)
                response = stub.RegisterReplica(request)
                # self.replica_list = response.replica_list
                assert response.success
            self.start_heartbeat_loop() # begin sending heartbeat requests to leader
        print(f"    ChatService __init__: replica_list={self.replica_list}")

        # TODO: Later. Merge users and messages from leader and persistent storage (need to discuss)

    def LoginUsername(self, request, context):
        """Handles username lookup to check if a user exists."""
        print("Calling LoginUsername")
        username = request.username
        user_exists = check_username_exists(username, self.users_dict) is not None
        return chat_pb2.LoginUsernameResponse(user_exists=user_exists, username=username)

    def LoginPassword(self, request, context):
        """Handles login by verifying the hashed password."""
        print("Calling LoginPassword")
        username = request.username
        password = request.password

        uid = check_username_exists(username, self.users_dict)
        if uid: # Existing account
            print(f'    Existing account: {uid}')
            print(f"    Password is correct:",check_username_password(uid, password, self.users_dict))
            if check_username_password(uid, password, self.users_dict): # Password is correct
                return chat_pb2.LoginPasswordResponse(success=True, uid=uid)
            else: # Password incorrect
                return chat_pb2.LoginPasswordResponse(success=False, uid=uid)
        else: # Create account
            print(f'    Creating account')
            uid = create_account(username, password, self.users_dict)
            save_users_and_messages(self.local_ip, self.local_port, self.users_dict, self.messages_dict)
            self.update_replicas(push_users = True, push_messages = False)
            return chat_pb2.LoginPasswordResponse(success=True, uid=uid)
        
    def update_replicas(self, push_users, push_messages):
        for replica_address in self.replica_list:
            if replica_address != self.leader_address:
                # push updates to replicas
                if push_messages: self.push_messages_to_replica(replica_address, self.messages_dict)
                if push_users: self.push_users_to_replica(replica_address, self.users_dict)

    def DeleteAccount(self, request, context):
        """Deletes a user account by UID."""
        print("Calling DeleteAccount")
        uid = request.uid
        success = delete_account(self.users_dict, uid)
        save_users_and_messages(self.local_ip, self.local_port, self.users_dict, self.messages_dict)
        self.update_replicas(push_users = True, push_messages = False)
        return chat_pb2.DeleteAccountResponse(success=success)
   
    def ListAccounts(self, request, context):
        """Returns a list of account usernames matching a wildcard search."""
        print("Calling LoginPassword")
        wildcard = request.wildcard
        accounts = list_accounts(self.users_dict, wildcard=wildcard)
        return chat_pb2.ListAccountsResponse(accounts=accounts)
    
    def SendMessage(self, request, context):
        """Handles sending a message from one user to another."""
        print("Calling SendMessage")
        message_sent = send_message(request.sender, request.receiver_username, request.text, self.users_dict, self.messages_dict, timestamp=request.timestamp)
        save_users_and_messages(self.local_ip, self.local_port, self.users_dict, self.messages_dict)
        self.update_replicas(push_users = True, push_messages = True)
        return chat_pb2.SendMessageResponse(success=message_sent)

    def GetSentMessages(self, request, context):
        """Retrieves the list of message IDs sent by a user."""
        print("Calling GetSentMessages")
        uid = request.uid
        mids = get_sent_messages_id(uid, self.users_dict)
        return chat_pb2.GetMessagesResponse(mids=mids)

    def GetReceivedMessages(self, request, context):
        """Retrieves the list of message IDs received by a user."""
        print("Calling GetReceivedMessages")
        uid = request.uid
        mids = get_received_messages_id(uid, self.users_dict)
        return chat_pb2.GetMessagesResponse(mids=mids)

    def GetMessageByMid(self, request, context):
        """Fetches the content of a message using its message ID."""
        print("Calling GetMessageByMid")
        message = get_message_by_mid(request.mid, self.messages_dict)
        return chat_pb2.GetMessageResponse(sender_uid=message["sender"], receiver_uid=message["receiver"], 
                                           sender_username=message["sender_username"], receiver_username=message["receiver_username"], 
                                           text=message["text"], timestamp=message["timestamp"], receiver_read=message["receiver_read"])

    def MarkMessageRead(self, request, context):
        """Marks a specific message as read."""
        print("Calling MarkMessageRead")
        mid = request.mid
        success = mark_message_read(self.messages_dict, mid)
        save_users_and_messages(self.local_ip, self.local_port, self.users_dict, self.messages_dict)
        self.update_replicas(push_users = False, push_messages = True)
        return chat_pb2.MarkMessageReadResponse(success=success)

    def DeleteMessages(self, request, context):
        """Deletes multiple messages for a given user."""
        print("Calling DeleteMessages")
        success, _ = delete_messages(self.users_dict, self.messages_dict, request.mids, uid=request.uid)
        save_users_and_messages(self.local_ip, self.local_port, self.users_dict, self.messages_dict)
        self.update_replicas(push_users = True, push_messages = True)
        return chat_pb2.DeleteMessagesResponse(success=success)
    
    def push_messages_to_replica(self, replica_address, messages_dict):
        print("Calling push_messages_to_replica")
        with grpc.insecure_channel(replica_address) as channel:
            stub = chat_pb2_grpc.ChatServiceStub(channel)
            messages = object_to_protobuf_list(messages_dict, chat_pb2.MessageData)
            print(f"    Preparing to send {len(messages)} messages to {replica_address}")
            request = chat_pb2.MessageSyncRequest(messages=messages)
            response = stub.SyncMessagesFromLeader(request)
            assert response.success

    def push_users_to_replica(self, replica_address, users_dict):
        print("Calling push_users_to_replica")
        with grpc.insecure_channel(replica_address) as channel:
            stub = chat_pb2_grpc.ChatServiceStub(channel)
            users = object_to_protobuf_list(users_dict, chat_pb2.UserData)
            print(f"    Preparing to send {len(users)} users to {replica_address}")
            request = chat_pb2.UserSyncRequest(users=users)
            response = stub.SyncUsersFromLeader(request)
            assert response.success

    def push_replica_list_to_replica(self, replica_address):
        print("Calling push_replica_list_to_replica")
        with grpc.insecure_channel(replica_address) as channel:
                stub = chat_pb2_grpc.ChatServiceStub(channel)
                print(f"    Preparing to send {len(self.replica_list)} replicas to {replica_address}")
                request = chat_pb2.ReplicaListSyncRequest(replica_list=self.replica_list)
                response = stub.SyncReplicaListFromLeader(request)
                assert response.success

    def RegisterReplica(self, request, context):
        print("Calling RegisterReplica")

        # Add replica to replica_list
        replica_address = f"{request.ip_address}:{request.port}"
        if replica_address not in self.replica_list:
            self.replica_list.append(replica_address)
        print(f"    Added replica to replica_list: self.replica_list={self.replica_list}")

        # Push messages and users to new replica
        self.push_messages_to_replica(replica_address, self.messages_dict)
        self.push_users_to_replica(replica_address, self.users_dict)
        print(f"    Pushed messages and users to replica")

        # Push replica _list to old replicas
        for replica_address in self.replica_list:
            if replica_address != self.leader_address:
                # Only send updated replicas to non-leaders
                self.push_replica_list_to_replica(replica_address)

        return chat_pb2.RegisterReplicaResponse(success=True)
    
    def Heartbeat(self, request, context):
        # print(f"Calling Heartbeat request from {request.server_id}")
        return chat_pb2.HeartbeatResponse(success=True)
    
    def SyncMessagesFromLeader(self, request, context):
        """Leader calls replica's SyncMessagesFromLeader to push messages."""
        print("Calling SyncMessagesFromLeader")
        self.messages_dict = protobuf_list_to_object(request.messages, Message, "mid")
        print(f"    Received {len(request.messages)} messages from leader server")
        save_users_and_messages(self.local_ip, self.local_port, self.users_dict, self.messages_dict)
        # TODO: Directly saving leader's message_dict. Need to merge with persistant version   
        return chat_pb2.MessageSyncResponse(success=True)

    def SyncUsersFromLeader(self, request, context):
        """Leader calls replica's SyncUsersFromLeader to push users."""
        print("Calling SyncUsersFromLeader")
        print(f"    Received {len(request.users)} users from leader server")
        self.users_dict = protobuf_list_to_object(request.users, User, "uid")
        save_users_and_messages(self.local_ip, self.local_port, self.users_dict, self.messages_dict)
        # TODO: Directly saving leader's message_dict. Need to merge with persistant version   
        return chat_pb2.UserSyncResponse(success=True)
    
    def SyncReplicaListFromLeader(self, request, context):
        print("Calling SyncReplicaListFromLeader")
        self.replica_list = request.replica_list
        print(f"    Updated replica_list to {self.replica_list}")
        return chat_pb2.ReplicaListSyncResponse(success=True)
    
    def GetReplicaList(self, request, context):
        print("Calling GetReplicaList")
        return chat_pb2.ReplicaListResponse(
            leader_address=self.leader_address,
            replica_list=self.replica_list
        )

def get_local_ip():
    """Safely get the LAN IP address of the current machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable, just used to get the correct local IP
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def serve(args):
    """Starts the gRPC server with only login flow."""
    # Leader and server addresses
    leader_ip, leader_port = args.leader_address.split(":")

    local_ip = socket.gethostbyname(get_local_ip()) if not args.is_leader else leader_ip
    local_port = args.port if not args.is_leader else leader_port

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_service = ChatService(args.is_leader, local_ip, local_port, leader_ip, leader_port, args.hi)
    chat_pb2_grpc.add_ChatServiceServicer_to_server(chat_service, server)

    if args.is_leader:
        server.add_insecure_port(f"{HOST}:{leader_port}")  # Leader uses HOST and PORT from config.ini
        print("Mode: leader, leader IP:", f"{leader_ip}:{leader_port}")
    else:
        server.add_insecure_port(f"{local_ip}:{local_port}")  # Replica uses local ip and port from arguments
        server.add_insecure_port(f"{HOST}:{local_port}") # Listen externally in case this one becomes leader later on
        print("Mode: replica, replica IP", f"{local_ip}:{local_port}", "leader IP", f"{leader_ip}:{leader_port}")

    server.start()
    chat_service.on_server_start()

    
    print(f"Server Proto started on port {leader_port}...")
    server.wait_for_termination()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the Chat Client with optional parameters.")
    parser.add_argument("--is-leader", action="store_true", help="Set this flag to run as a leader")
    parser.add_argument("--port", type=int, default=60001, help="Specify the port")
    parser.add_argument("--hi", type=int, default=1)
    parser.add_argument("--leader-address", type=str, default="10.250.248.221:60000", help="Specify the leader address")

    args = parser.parse_args()
    serve(args)