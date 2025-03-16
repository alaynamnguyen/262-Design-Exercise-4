import json 

opcode_to_task = {
    "a": "login-username",
    "b": "login-username-reply",
    "c": "login-password",
    "d": "login-password-reply",
    "e": "list-accounts",
    "f": "list-accounts-reply",
    "g": "send-message",
    "h": "send-message-reply",
    "i": "get-sent-messages",
    "j": "get-sent-messages-reply",
    "k": "get-received-messages",
    "l": "get-received-messages-reply",
    "m": "get-message-by-mid",
    "n": "get-message-by-mid-reply",
    "o": "mark-message-read",
    "p": "mark-message-read-reply",
    "q": "delete-messages",
    "r": "delete-messages-reply",
    "s": "delete-account",
    "t": "delete-account-reply",
}

task_to_opcode = {v: k for k, v in opcode_to_task.items()}

# Utility Functions for JSON/Wire Protocol Handling
def send_response(data, response, USE_WIRE_PROTOCOL):
    """Encapsulates response handling for JSON or wire protocol."""
    if USE_WIRE_PROTOCOL:
        encoded_response = json_to_wire_protocol(response)
    else:
        encoded_response = json.dumps(response).encode("utf-8")
    data.outb += encoded_response

def parse_request(data, USE_WIRE_PROTOCOL):
    """Encapsulates request handling for JSON or wire protocol."""
    if USE_WIRE_PROTOCOL:
        return wire_protocol_to_json(data.inb.decode("utf-8")) # TODO update, Placeholder for wire protocol decoding
    return json.loads(data.inb.decode("utf-8"))

def json_to_wire_protocol(json_message):
    """
    Encodes a JSON message into a wire protocol format.

    Args:
        json_message (dict): The JSON message to be encoded.

    Returns:
        bytes: The encoded message in wire protocol format.
    """
    wire_message = f"{task_to_opcode[json_message['task']]}"

    if json_message["task"] == "login-username":
        wire_message += json_message["username"]

    elif json_message["task"] == "login-username-reply":
        user_exists = str(json_message["user_exists"])[0]
        wire_message += user_exists + \
            str(json_message["username"])

    elif json_message["task"] == "login-password":
        username_length = f'{len(json_message["username"]):02}'
        wire_message += username_length + \
            json_message["username"] + \
            json_message["password"]
        
    elif json_message["task"] == "login-password-reply":
        login_success = str(json_message["login_success"])[0]
        # Note len(uuid) = 36
        wire_message += login_success + \
            json_message["uid"]
        
    elif json_message["task"] == "list-accounts":
        wire_message += json_message["wildcard"]

    elif json_message["task"] == "list-accounts-reply":
        accounts_str = ""
        accounts_list = json_message["accounts"]
        for account in accounts_list:
            username_length = f'{len(account):02}'
            accounts_str += username_length + account
        wire_message += accounts_str
        
    elif json_message["task"] == "list-accounts":
        wire_message += json_message["wildcard"]

    elif json_message["task"] == "list-accounts-reply":
        accounts_str = ""
        accounts_list = json_message["accounts"]
        for account in accounts_list:
            username_length = f'{len(account):02}'
            accounts_str += username_length + account
        wire_message += accounts_str

    elif json_message["task"] == "send-message":
        # len(datetime.now) = 26
        # [op][sender_uid 36][timestamp 26][receiver uname length][receipient uname][message]
        receiver_username_length = f'{len(json_message["receiver"]):02}'
        wire_message += json_message["sender"] + \
            json_message["timestamp"] + \
            receiver_username_length + \
            json_message["receiver"] + \
            json_message["text"]

    elif json_message["task"] == "send-message-reply":
        wire_message += str(json_message["success"])[0]
    
    elif json_message["task"] == "get-sent-messages" or json_message["task"] == "get-received-messages":
        wire_message += json_message["sender"]

    elif json_message["task"] == "get-sent-messages-reply" or json_message["task"] == "get-received-messages-reply":
        # [op][uid 36][comma separated mids]
        wire_message += json_message["uid"]
        wire_message += ",".join(json_message["mids"])

    elif json_message["task"] == "get-message-by-mid":
        wire_message += json_message["mid"]

    elif json_message["task"] == "get-message-by-mid-reply":
        # [op][sender uid 36][receiver uid 36][mid 36][timestamp 26][T/F receiver]
        # [len 2][sender username][len 2][receiver username][message is rest]]
        print("JSON Message", json_message)
        message = json_message["message"]
        print("Message", message)
        sender_len = f'{len(message["sender_username"]):02}'
        receiver_len = f'{len(message["receiver_username"]):02}'
        receiver_read = str(message["receiver_read"])[0]

        wire_message += message["sender"] + \
            message["receiver"] + \
            message["mid"] + \
            message["timestamp"] + \
            receiver_read + \
            sender_len + \
            message["sender_username"] + \
            receiver_len + \
            message["receiver_username"] + \
            message["text"]

    elif json_message["task"] == "mark-message-read":
        wire_message += json_message["mid"]

    elif json_message["task"] == "mark-message-read-reply" or json_message["task"] == "delete-messages-reply":
        wire_message += str(json_message["success"])[0]
    
    elif json_message["task"] == "delete-messages":
        # [op][mid 36][uid 36]
        wire_message += json_message["uid"] + \
            ",".join(json_message["mids"])
    
    elif json_message["task"] == "delete-account":
        wire_message += json_message["uid"]

    elif json_message["task"] == "delete-account-reply":
        wire_message += str(json_message["success"])[0]

    else:
        raise NotImplementedError
    print("Wire message constructed:", wire_message)
    return wire_message.encode("utf-8")

def wire_protocol_to_json(wire_message):
    """
    Decodes a wire protocol message into JSON format.

    Args:
        wire_message (bytes): The encoded message in wire protocol format.

    Returns:
        dict: The decoded message in JSON format.
    """    
    print("Wire message received:", wire_message)
    json_message = {
        "task": opcode_to_task[wire_message[0]]
    }

    if json_message["task"] == "login-username":
        json_message["username"] = wire_message[1:]

    elif json_message["task"] == "login-username-reply":
        json_message["user_exists"] = (wire_message[1] == "T")
        json_message["username"] = wire_message[2:]

    elif json_message["task"] == "login-password":
        username_length = int(wire_message[1:3])
        json_message["username"] = wire_message[3:username_length+3]
        json_message["password"] = wire_message[username_length+3:]
    
    elif json_message["task"] == "login-password-reply":
        json_message["login_success"] = (wire_message[1] == "T")
        json_message["uid"] = wire_message[2: 2+36]

    elif json_message["task"] == "list-accounts":
        json_message["wildcard"] = wire_message[1:]

    elif json_message["task"] == "list-accounts-reply":
        if len(wire_message) <= 3:  # No accounts returned ([op code][2 digit username length])
            json_message["accounts"] = []
        else:
            i = 1
            accounts_list = []
            while i != len(wire_message):
                username_length = int(wire_message[i:i+2])
                username = wire_message[i+2:i+2+username_length]
                if len(username) > 0: accounts_list.append(username)
                i += 2 + username_length
            json_message["accounts"] = accounts_list

    elif json_message["task"] == "send-message":
        # [op][client_uid 36][timestamp 26][receiver uname length][receipient uname][message]
        json_message["sender"] = wire_message[1:37]
        json_message["timestamp"] = wire_message[37:63]
        receiver_length = int(wire_message[63:65])
        json_message["receiver"] = wire_message[65:65+receiver_length]
        json_message["text"] = wire_message[65+receiver_length:]

    elif json_message["task"] == "send-message-reply":
        json_message["success"] = (wire_message[1] == "T")
    
    elif json_message["task"] == "get-sent-messages" or json_message["task"] == "get-received-messages":
        json_message["sender"] = wire_message[1:]

    elif json_message["task"] == "get-sent-messages-reply" or json_message["task"] == "get-received-messages-reply":
        # [op][uid 36][comma separated mids]
        json_message["uid"] = wire_message[1:37]
        if len(wire_message) <= 37:
            json_message["mids"] = []
        else:
            json_message["mids"] = wire_message[37:].split(",")

    elif json_message["task"] == "get-message-by-mid":
        # [op][mid 36]
        json_message["mid"] = wire_message[1:]

    elif json_message["task"] == "get-message-by-mid-reply":
        # [op][sender uid 36][receiver uid 36][mid 36][timestamp 26][T/F receiver]
        # [len 2][sender username][len 2][receiver username][message is rest]]
        message = dict()
        message["sender"] = wire_message[1:1+36]
        message["receiver"] = wire_message[37:37+36]
        message["mid"] = wire_message[73:73+36]
        message["timestamp"] = wire_message[109:109+26]
        message["receiver_read"] = (wire_message[135] == "T")
        
        sender_len = int(wire_message[136:138])
        message["sender_username"] = wire_message[138:138+sender_len]
        receiver_len = int(wire_message[138+sender_len:140+sender_len])
        message["receiver_username"] = wire_message[140+sender_len:140+sender_len+receiver_len]
        message["text"] = wire_message[140+sender_len+receiver_len:]

        json_message["message"] = message

    elif json_message["task"] == "mark-message-read":
        json_message["mid"] = wire_message[1:]

    elif json_message["task"] == "mark-message-read-reply" or json_message["task"] == "delete-messages-reply":
        json_message["success"] = (wire_message[1] == "T")
    
    elif json_message["task"] == "delete-messages":
        json_message["uid"] = wire_message[1:37]
        json_message["mids"] = wire_message[37:].split(",")

    
    elif json_message["task"] == "delete-account":
        json_message["uid"] = wire_message[1:]

    elif json_message["task"] == "delete-account-reply":
        json_message["success"] = (wire_message[1] == "T")
        json_message["uid"] = wire_message[2:]
    else:
        raise NotImplementedError
    
    return json_message

# Recursive function for object to dict
def object_to_dict_recursive(obj):
    """Recursively converts objects to dictionaries."""
    if hasattr(obj, "__dict__"):
        return {key: object_to_dict_recursive(value) for key, value in vars(obj).items()}
    return obj

# Recursive function for dict to object
def dict_to_object_recursive(dct, cls):
    """Converts a dictionary back to an object of type cls."""
    obj = cls.__new__(cls)  # Create an empty instance
    for key, value in dct.items():
        setattr(obj, key, dict_to_object_recursive(value, globals().get(cls.__name__, object)) if isinstance(value, dict) else value)
    return obj