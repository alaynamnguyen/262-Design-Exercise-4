import uuid
import json

class User:
    """
    Represents a user in the system.

    Attributes:
    ----------
    uid : str
        The unique identifier of the user. Defaults to a randomly generated UUID.
    username : str
        The username of the user.
    password : str
        The password of the user.
    received_messages : list
        A list of message IDs that the user has received.
    sent_messages : list
        A list of message IDs that the user has sent.
    active : bool
        Indicates whether the user account is active. Defaults to True.
    """

    def __init__(self, username, password, uid=None, active=True, received_messages=None, sent_messages=None):
        """
        Initializes a User object with a username, password, and optional user ID.

        Parameters:
        ----------
        username : str
            The username of the user.
        password : str
            The password of the user.
        uid : str, optional
            The unique identifier for the user. If not provided, a UUID is generated.
        active : bool, optional
            Indicates whether the user account is active. Defaults to True.
        """
        self.uid = str(uid) if uid else str(uuid.uuid4())
        self.username = str(username)
        self.password = str(password)
        self.received_messages = list(received_messages) if received_messages is not None else []
        self.sent_messages = list(sent_messages) if sent_messages is not None else []
        self.active = bool(active)

    def __repr__(self):
        """
        Returns a string representation of the User object.

        Returns:
        -------
        str
            A formatted string containing the user's details.
        """
        return f"User(uid={self.uid}, username={self.username}, password={self.password}, received_messages={self.received_messages}, sent_messages={self.sent_messages}, active={self.active})"