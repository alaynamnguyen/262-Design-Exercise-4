from model import User
from utils import send_response

def check_username_exists(username: str, users_dict: dict):
    """
    Checks if a given username exists in the accounts dictionary and is active.
    """
    print("Calling check_username_exists")
    for uid, user in users_dict.items():
        if user.username == username and user.active:
            return uid
    return None

def check_username_password(uid: str, password: str, users_dict: dict):
    """
    Validates if the provided password matches the stored password for a given user ID.
    """
    print("Calling check_username_password")
    return users_dict[uid].password == password

def create_account(username: str, password: str, users_dict: dict):
    """
    Creates a new user account with the given username and password.
    """
    print("Calling create_account")
    if check_username_exists(username, users_dict):
        return None

    user = User(username, password) 
    users_dict[user.uid] = user
    return user.uid

def mark_client_connected(uid, addr, connected_clients, sock):
    """
    Marks a client as connected by storing their address and socket information.
    """
    connected_clients[uid] = [addr, sock] # Mark this client as logged in and online
    # print("Connected clients:", connected_clients.keys())

def handle_login_request(data, sock, message, users_dict, connected_clients, USE_WIRE_PROTOCOL):
    """
    Handles a client login request, processing both username and password authentication.
    """
        
    print("Calling handle_login_request")
    response = {}
    if message["task"] == "login-username":
        print("Handling login-username")
        uid = check_username_exists(message["username"], users_dict)
        response = {
            "task": "login-username-reply",
            "username": message["username"], # TODO return uid instead?
            "user_exists": uid is not None
        }
    elif message["task"] == "login-password":
        print("Handling login-password")
        
        uid = check_username_exists(message["username"], users_dict)
        if uid: # Username exists
            if check_username_password(uid, message["password"], users_dict): # Password is correct
                response = {
                    "task": "login-password-reply",
                    "uid": uid,
                    "login_success": True
                }
                mark_client_connected(uid, data.addr, connected_clients, sock)
            else: # Password is incorrect
                response = {
                    "task": "login-password-reply",
                    "uid": uid,
                    "login_success": False
                }
        else: # Username does not exist
            uid = create_account(message["username"], message["password"], users_dict)
            print("UID:", uid)
            response = {
                "task": "login-password-reply",
                "uid": uid,
                "login_success": True
            }
            mark_client_connected(uid, data.addr, connected_clients, sock)

    send_response(data, response, USE_WIRE_PROTOCOL)
