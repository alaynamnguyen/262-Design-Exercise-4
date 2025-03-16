from utils import hash_password
from .communication import build_and_send_task

def check_username(sock, username, use_wire_protocol):
    """
    Checks whether a given username exists on the server.
    """
    response = build_and_send_task(sock, "login-username", username=username, use_wire_protocol=use_wire_protocol)
    return response["user_exists"]

def login_user(sock, username, password, use_wire_protocol):
    """
    Attempts to authenticate an existing user with the provided credentials.
    """
    hashed_password = hash_password(password)
    response = build_and_send_task(sock, "login-password", username=username, password=hashed_password, use_wire_protocol=use_wire_protocol)
    return response

def create_account(sock, username, password, use_wire_protocol):
    """
    Attempts to create a new user account with the provided username and password.
    """
    hashed_password = hash_password(password)
    response = build_and_send_task(sock, "login-password", username=username, password=hashed_password, use_wire_protocol=use_wire_protocol)
    return response

def cli_login(sock):
    """
    Handles user authentication via command-line input, allowing login or account creation.
    """
    while True:
        username = input("Username: ").strip()
        user_exists = check_username(sock, username)

        if user_exists:  # Login with existing account
            print("User exists.")
            while True:
                password = input("Password: ").strip()
                response = login_user(sock, username, password)
                if response["login_success"]:
                    print(f"Login successful. You have {len(response['unread_messages'])} unread messages.")
                    return response["uid"]
                else:
                    print("Incorrect password. Please try again.")
        else:  # Create a new account
            print("Username does not exist. Creating a new account.")
            while True:
                password = input("Create a password: ").strip()
                response = create_account(sock, username, password)
                if response["login_success"]:
                    print("Account created successfully.")
                    return response["uid"]
                else:
                    print("Failed to create account. Please try again.")
