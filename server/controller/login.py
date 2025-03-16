from model import User

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