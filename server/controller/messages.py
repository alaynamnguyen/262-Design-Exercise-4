from model import Message
from utils import object_to_dict_recursive

def send_message(sender_uid, receiver_username, text, users_dict, messages_dict, timestamp, connected_clients=None): 
    """
    Sends a message from a sender to a recipient. If the recipient is online, they are notified immediately.
    """
    print("Calling send message", receiver_username)
    receiver_uid = None
    for uid, user in users_dict.items():
        if user.username == receiver_username and user.active:
            receiver_uid = uid
    sender_username = users_dict[sender_uid].username

    if receiver_uid is None:
        print("Receiver does not exist.")
        return False

    # Create message object, receiver_read is False by default
    message = Message(sender=sender_uid, receiver=receiver_uid, sender_username=sender_username, receiver_username=receiver_username, text=text, timestamp=timestamp)
    print("Message id:", message.mid)

    # Update runtime storage
    messages_dict[message.mid] = message
    users_dict[sender_uid].sent_messages.append(message.mid)
    users_dict[receiver_uid].received_messages.append(message.mid)

    return True

def delete_messages(users_dict, messages_dict, mids, uid):
    """
    Deletes messages from a user's sent and received messages lists.
    """

    deleted_mids = []
    success = True
    for mid in mids:
        if mid in messages_dict: # found message to delete
            # Remove message if found in sent
            if mid in users_dict[uid].sent_messages:
                users_dict[uid].sent_messages.remove(mid)
            # Remove message if found in received
            if mid in users_dict[uid].received_messages:
                users_dict[uid].received_messages.remove(mid)

            deleted_mids.append(mid)
        else:
            print(f"Message {mid} does not exist.")
            success = False

    return success, deleted_mids

def mark_message_read(messages_dict, mid):
    """
    Marks a message as read by updating its read status.
    """
    if mid in messages_dict:
        messages_dict[mid].receiver_read = True
        return True
    else:
        print(f"Failed to mark message read: message {mid} does not exist.")
        return False
    
def get_message_by_mid(mid, messages_dict):
    """
    Retrieves a message by its unique identifier and converts it to a dictionary.
    """
    if mid in messages_dict:
        return object_to_dict_recursive(messages_dict[mid]) # Convert to dict
    else:
        print(f"Message {mid} does not exist.")
        return None  # TODO Handle missing message case
    
def get_sent_messages_id(uid, users_dict):
    """
    Retrieves the message IDs of all messages sent by a specific user.
    """
    return users_dict[uid].sent_messages

def get_received_messages_id(uid, users_dict):
    """
    Retrieves the message IDs of all messages received by a specific user.
    """
    return users_dict[uid].received_messages
