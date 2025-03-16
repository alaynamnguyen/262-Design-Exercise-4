from datetime import datetime
import uuid

class Message:
    """
    Represents a message exchanged between users.

    Attributes:
    ----------
    sender : str
        The unique identifier of the sender.
    receiver : str
        The unique identifier of the receiver.
    sender_username : str
        The username of the sender.
    receiver_username : str
        The username of the receiver.
    text : str
        The text content of the message.
    mid : str
        The unique identifier of the message. Defaults to a randomly generated UUID.
    timestamp : str
        The time when the message was sent, stored as a string for serialization.
    receiver_read : bool
        Indicates whether the receiver has read the message. Defaults to False.
    """

    def __init__(self, sender, receiver, sender_username, receiver_username, text, mid=None, timestamp=None, receiver_read=False):
        """
        Initializes a new message.

        Parameters:
        ----------
        sender : str
            The unique identifier of the sender.
        receiver : str
            The unique identifier of the receiver.
        sender_username : str
            The username of the sender.
        receiver_username : str
            The username of the receiver.
        text : str
            The content of the message.
        mid : str, optional
            The unique identifier of the message. If not provided, a UUID is generated.
        timestamp : datetime, optional
            The time the message was sent. Defaults to the current time.
        receiver_read : bool, optional
            Whether the receiver has read the message. Defaults to False.
        """
        self.sender = sender
        self.receiver = receiver
        self.sender_username = sender_username
        self.receiver_username = receiver_username
        self.text = text
        self.mid = mid if mid else str(uuid.uuid4())
        self.timestamp = str(timestamp if timestamp else datetime.now())  # Convert to string for JSON serialization
        self.receiver_read = receiver_read

    def mark_as_read(self):
        """
        Marks the message as read by the receiver.
        """
        self.receiver_read = True

    def __repr__(self):
        """
        Returns a string representation of the message.

        Returns:
        -------
        str
            A formatted string containing the message details.
        """
        return (f"Message(mid={self.mid}, sender={self.sender}, receiver={self.receiver}, "
                f"timestamp={self.timestamp}, text={self.text}, receiver_read={self.receiver_read})")