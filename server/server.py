import socket
import selectors
import types
import configparser
import json
from model import User, Message
from controller.login import handle_login_request
from controller.accounts import list_accounts, delete_account
from controller.messages import send_message, get_sent_messages_id, get_received_messages_id, delete_messages, mark_message_read, get_message_by_mid
from utils import dict_to_object_recursive, object_to_dict_recursive, parse_request, send_response

# Load config
config = configparser.ConfigParser()
config.read("config.ini")

HOST = config["network"]["host"]
PORT = int(config["network"]["port"])
USE_WIRE_PROTOCOL = config.getboolean("network", "use_wire_protocol")

sel = selectors.DefaultSelector()

# User dict
users_dict = dict()
# TODO use data instead of test
with open("server/test/user.json", "r") as f:
        users = json.load(f)
for k, v in users.items():
    user = dict_to_object_recursive(v, User)
    users_dict[user.uid] = user

# Message dict
messages_dict = dict()
# TODO use data instead of test
with open("server/test/message.json", "r") as f:
    messages = json.load(f)
for k, v in messages.items():
    message = dict_to_object_recursive(v, Message)
    messages_dict[message.mid] = message

# Keep track of connected, logged in clients by uid
connected_clients = dict() # uid --> [addr, sock]

# For ease of seeing that things are deleted/added properly
def write_users_messages_json(users_dict, messages_dict):
    """
    Saves the current state of users and messages to JSON files.

    Parameters:
    ----------
    users_dict : dict
        The dictionary storing user accounts.
    messages_dict : dict
        The dictionary storing messages.
    """
    with open("server/test/user.json", "w") as f:
        json.dump(users_dict, f, default=object_to_dict_recursive, indent=4)
    with open("server/test/message.json", "w") as f:
        json.dump(messages_dict, f, default=object_to_dict_recursive, indent=4)

def accept_wrapper(sock):
    """
    Accepts a new client connection and registers it with the selector.

    Parameters:
    ----------
    sock : socket
        The server socket that listens for incoming connections.
    """
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    """
    Processes incoming client requests, including login, messaging, and account management.

    Parameters:
    ----------
    key : selectors.SelectorKey
        The selector key representing the client socket.
    mask : int
        The I/O event mask indicating the readiness of the socket.
    """
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.inb += recv_data
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()

            for client_uid, value in connected_clients.items():
                client_addr, _ = value
                if client_addr == data.addr: # Only remove the client who disconnected
                    print(f"Removing {client_uid} from connected_clients")
                    connected_clients.pop(client_uid)
                    break  # Stop after removing the correct UID

        if data.inb:
            message = parse_request(data, USE_WIRE_PROTOCOL)
            if message["task"].startswith("login"):
                print("Calling handle_login_request")
                handle_login_request(data, sock, message, users_dict, connected_clients, USE_WIRE_PROTOCOL)
            elif message["task"] == "list-accounts":
                print("Calling list_accounts")
                response = {
                    "task": "list-accounts-reply",
                    "accounts": list_accounts(users_dict, wildcard=message["wildcard"])
                }
                send_response(data, response, USE_WIRE_PROTOCOL)
            elif message["task"] == "send-message":
                print("Send message request: ", message)
                message_sent = send_message(message["sender"], message["receiver"], message["text"], users_dict, messages_dict, timestamp=message["timestamp"], connected_clients=connected_clients)
                response = {
                    "task": "send-message-reply",
                    "success": message_sent
                }
                send_response(data, response, USE_WIRE_PROTOCOL)
            elif message["task"] == "get-sent-messages":
                print(f"Get sent messages request from {message['sender']}")
                response = {
                    "task": "get-sent-messages-reply",
                    "uid": message["sender"],
                    "mids": get_sent_messages_id(message["sender"], users_dict)
                }
                send_response(data, response, USE_WIRE_PROTOCOL)
            elif message["task"] == "get-received-messages":
                print(f"Get received messages request from {message['sender']}")
                response = {
                    "task": "get-received-messages-reply",
                    "uid": message["sender"],
                    "mids": get_received_messages_id(message["sender"], users_dict)
                }
                send_response(data, response, USE_WIRE_PROTOCOL)
            elif message["task"] == "get-message-by-mid":
                print(f"Get message by mid request for {message['mid']}")
                response = {
                    "task": "get-message-by-mid-reply",
                    "message": get_message_by_mid(message["mid"], messages_dict)
                }
                send_response(data, response, USE_WIRE_PROTOCOL)
            elif message["task"] == "mark-message-read":
                print(f"Mark message read request for {message['mid']}")
                response = {
                    "task": "mark-message-read-reply",
                    "success": mark_message_read(messages_dict, message["mid"])
                }
                print("Updated message:", messages_dict[message["mid"]])
                send_response(data, response, USE_WIRE_PROTOCOL)
            elif message["task"] == "delete-messages":
                print("Delete messages request:", message)
                success, _ = delete_messages(users_dict, messages_dict, message["mids"], uid=message["uid"])
                response = {
                    "task": "delete-messages-reply",
                    "success": success
                }
                send_response(data, response, USE_WIRE_PROTOCOL)
            elif message["task"] == "delete-account":
                print("Delete account request:", message)
                response = {
                    "task": "delete-account-reply",
                    "success": delete_account(users_dict, message["uid"])
                }
                send_response(data, response, USE_WIRE_PROTOCOL)
            
            data.inb = b""
        
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print("Sending DATA: ", data.outb)
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

if __name__ == "__main__":
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((HOST, PORT))
    lsock.listen()
    print(f"Listening on {HOST}:{PORT}")
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        # Save runtime storage to disk before exiting
        write_users_messages_json(users_dict, messages_dict)
        print("Caught keyboard interrupt, exiting (saved runtime storage to disk)")
    finally:
        sel.close()
