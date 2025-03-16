import json
import hashlib

def send_request(sock, json_message, use_wire_protocol):
    """Sends a JSON message, encoding it to wire protocol if needed."""
    if use_wire_protocol:
        print("Using wire protocol")
        encoded_message = json_to_wire_protocol(json_message)
    else:
        print("Using JSON protocol")
        encoded_message = json.dumps(json_message).encode("utf-8")
    sock.sendall(encoded_message)

def receive_response(sock, use_wire_protocol):
    """Receives a response, decoding from wire protocol if needed."""
    response_data = sock.recv(1024)
    if use_wire_protocol:
        return wire_protocol_to_json(response_data)
    return json.loads(response_data.decode("utf-8"))

def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()
