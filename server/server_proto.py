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
from utils import dict_to_object_recursive, object_to_dict_recursive, parse_request, send_response

# Load config
config = configparser.ConfigParser()
config.read("config.ini")

HOST = config["network"]["host"]
PORT = int(config["network"]["port"])

def load_users_and_messages():
    """Loads user data from the JSON file."""
    # User dict
    users_dict = dict()
    with open("server/test/user.json", "r") as f:
            users = json.load(f)
    for k, v in users.items():
        user = dict_to_object_recursive(v, User)
        users_dict[user.uid] = user

    messages_dict = dict()
    with open("server/test/message.json", "r") as f:
        messages = json.load(f)
    for k, v in messages.items():
        message = dict_to_object_recursive(v, Message)
        messages_dict[message.mid] = message
    
    return users_dict, messages_dict

def save_users(users_dict):
    """Saves user data to the JSON file."""
    with open("server/test/user.json", "w") as f:
        json.dump(users_dict, f, default=object_to_dict_recursive, indent=4)

def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

class ChatService(chat_pb2_grpc.ChatServiceServicer):
    
    def __init__(self):
        """Initializes the ChatService with user and message data."""
        self.users_dict, self.messages_dict = load_users_and_messages()

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
    
def serve():
    """Starts the gRPC server with only login flow."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatService(), server)
    server_address = f"{HOST}:{PORT}"  # Use HOST and PORT from config.ini
    server.add_insecure_port(server_address)
    server.start()
    print(f"Server Proto started on port {PORT}...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()