from .communication import build_and_send_task

def list_accounts(sock, wildcard, use_wire_protocol):
    """
    Retrieves a list of accounts from the server that match a specified wildcard pattern.
    """
    print("Calling list_accounts")
    response = build_and_send_task(sock, "list-accounts", use_wire_protocol, wildcard=wildcard)
    
def delete_account(sock, uid, use_wire_protocol):
    """
    Requests account deletion from the server for a specified user ID.
    """
    print("Calling delete_account")
    response = build_and_send_task(sock, "delete-account", use_wire_protocol, uid=uid)
    # print("Response:", response)
    return response
