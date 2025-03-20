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


# Load config
config = configparser.ConfigParser()
config.read("config.ini")

HOST = config["network"]["host"]
PORT = int(config["network"]["port"])

def load_users_and_messages():
    """Loads user data from the JSON file."""
    # User dict
    users_dict = dict()
    with open("server/data/user.json", "r") as f:
            users = json.load(f)
    for k, v in users.items():
        user = dict_to_object_recursive(v, User)
        users_dict[user.uid] = user

    # Message dict
    messages_dict = dict()
    with open("server/data/message.json", "r") as f:
        messages = json.load(f)
    for k, v in messages.items():
        message = dict_to_object_recursive(v, Message)
        messages_dict[message.mid] = message
    
    return users_dict, messages_dict

def save_users(users_dict):
    """Saves user data to the JSON file."""
    with open("server/data/user.json", "w") as f:
        json.dump(users_dict, f, default=object_to_dict_recursive, indent=4)

def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

class ChatService(chat_pb2_grpc.ChatServiceServicer):
    
    def __init__(self, is_leader, local_ip, local_port, leader_ip, leader_port):
        """Initializes the ChatService with user and message data."""
        self.is_leader = is_leader
        self.local_ip = local_ip
        self.local_port = local_port
        self.leader_ip = leader_ip
        self.leader_port = leader_port
        self.users_dict, self.messages_dict = load_users_and_messages() 
        # TODO: Replica load users and messages from process specific persistent storage
        # TODO: Merge users and messages from leader and persistent storage (need to discuss)

    def on_server_start(self):
        """Setup server when server starts"""
        if self.is_leader:  # Leader server initialization
            self.replica_list = [f"{HOST}:{PORT}"] # Leader is included in the replica_list
        else:  # Replica server initialization
            with grpc.insecure_channel(f"{self.leader_ip}:{self.leader_port}") as channel:
                stub = chat_pb2_grpc.ChatServiceStub(channel)
                request = chat_pb2.RegisterReplicaRequest(ip_address=self.local_ip, port=self.local_port)
                response = stub.RegisterReplica(request)
                self.replica_list = response.replica_list
        print(f"ChatService __init__: replica_list={self.replica_list}")

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
            print(f'Existing account: {uid}')
            print("Password is correct:",check_username_password(uid, password, self.users_dict))
            if check_username_password(uid, password, self.users_dict): # Password is correct
                return chat_pb2.LoginPasswordResponse(success=True, uid=uid)
            else: # Password incorrect
                return chat_pb2.LoginPasswordResponse(success=False, uid=uid)
        else: # Create account
            print('Running create account')
            uid = create_account(username, password, self.users_dict)
            return chat_pb2.LoginPasswordResponse(success=True, uid=uid)

    def DeleteAccount(self, request, context):
        """Deletes a user account by UID."""
        print("Calling DeleteAccount")
        uid = request.uid
        success = delete_account(self.users_dict, uid)
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
        return chat_pb2.GetMessageResponse(sender_uid=message["sender"], receiver_uid=message["receiver"], sender_username=message["sender_username"],
                                           receiver_username=message["receiver_username"], text=message["text"], timestamp=message["timestamp"], receiver_read=message["receiver_read"])

    def MarkMessageRead(self, request, context):
        """Marks a specific message as read."""
        print("Calling MarkMessageRead")
        mid = request.mid
        success = mark_message_read(self.messages_dict, mid)
        return chat_pb2.MarkMessageReadResponse(success=success)

    def DeleteMessages(self, request, context):
        """Deletes multiple messages for a given user."""
        print("Calling DeleteMessages")
        success, _ = delete_messages(self.users_dict, self.messages_dict, request.mids, uid=request.uid)
        return chat_pb2.DeleteMessagesResponse(success=success)
    
    def RegisterReplica(self, request, context):
        print("Calling RegisterReplica")

        # Add replica to replica_list
        replica_address = f"{request.ip_address}:{request.port}"
        if replica_address not in self.replica_list:
            self.replica_list.append(replica_address)
        print(f"RegisterReplica: self.replica_list={self.replica_list}")

        # Push messages to replica
        with grpc.insecure_channel(replica_address) as channel:
            stub = chat_pb2_grpc.ChatServiceStub(channel)
            # messages = [
            #     chat_pb2.MessageData(sender=m.sender, receiver=m.receiver,
            #                          sender_username=m.sender_username, receiver_username=m.receiver_username,
            #                          text=m.text, mid=m.mid, timestamp=m.timestamp, receiver_read=m.receiver_read)
            #     for m in self.messages_dict.values()
            # ]

            # Note: If a MessageData object's receiver_read is False, it is not printed. 
            #       Likely because it's MessageData's default value
            messages = object_to_protobuf_list(self.messages_dict, chat_pb2.MessageData)
            print(f"Preparing to send {len(messages)} messages to {replica_address}")
            request = chat_pb2.MessageSyncRequest(messages=messages)
            response = stub.SyncMessagesFromLeader(request)
            assert response.success

        # TODO: Push users to replica
        # TODO: Notify all replicas of new replica

        return chat_pb2.RegisterReplicaResponse(success=True, replica_list=self.replica_list)
    
    def SyncMessagesFromLeader(self, request, context):
        """Leader calls replica's SyncMessagesFromLeader to push messages."""
        print("Calling SyncMessagesFromLeader")
        self.messages_dict = protobuf_list_to_object(request.messages, Message, "mid")
        print(f"Received {len(request.messages)} from leader server") 
        # TODO: Directly saving leader's message_dict. Need to merge with persistant version   
        return chat_pb2.MessageSyncResponse(success=True)


def serve(args):
    """Starts the gRPC server with only login flow."""
    # Leader and server addresses
    local_ip = socket.gethostbyname(socket.gethostname())
    local_port = args.port

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_service = ChatService(args.is_leader, local_ip, local_port, HOST, PORT)
    chat_pb2_grpc.add_ChatServiceServicer_to_server(chat_service, server)

    if args.is_leader:
        server.add_insecure_port(f"{HOST}:{PORT}")  # Leader uses HOST and PORT from config.ini
        print("Leader mode, leader IP:", f"{HOST}:{PORT}")
    else:
        server.add_insecure_port(f"{local_ip}:{local_port}")  # Replica uses local ip and port from arguments
        print("Replica mode, replica IP", f"{local_ip}:{local_port}", "leader IP", f"{HOST}:{PORT}")

    server.start()
    chat_service.on_server_start()
    print(f"Server Proto started on port {PORT}...")
    server.wait_for_termination()
    # TODO: Implement leader election

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the Chat Client with optional parameters.")
    parser.add_argument("--is-leader", action="store_true", help="Set this flag to run as a leader")
    parser.add_argument("--port", type=int, default=65433, help="Specify the port")

    args = parser.parse_args()
    serve(args)