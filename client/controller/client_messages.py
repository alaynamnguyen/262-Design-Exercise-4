from .communication import build_and_send_task

def delete_messages(sock, mids, client_uid, use_wire_protocol):
    """
    Sends a request to delete specified messages from the server.
    """
    print("Calling delete_messages")
    response = build_and_send_task(sock, "delete-messages", use_wire_protocol, mids=mids, uid=client_uid)

    if response["success"]:
        print("Messages successfully deleted")
        return
    else:
        print("Failed to delete messages.")
        return # UI does not change
    
def mark_message_read(sock, mid, use_wire_protocol):
    """
    Sends a request to mark a specific message as read.
    """
    print("Calling mark_message_read")
    response = build_and_send_task(sock, "mark-message-read", use_wire_protocol, mid=mid)

    if response["success"]:
        print("Message marked as read.")