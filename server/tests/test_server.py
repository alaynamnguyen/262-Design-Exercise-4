import unittest
import selectors
import types
import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import MagicMock, patch
from server import accept_wrapper, service_connection, write_users_messages_json
from model.user import User
from model.message import Message

class TestServer(unittest.TestCase):

    @patch("server.sel")
    def test_accept_wrapper(self, mock_selector):
        """Test accepting a new client connection."""
        mock_sock = MagicMock()
        mock_conn = MagicMock()
        mock_sock.accept.return_value = (mock_conn, ("127.0.0.1", 50000))

        accept_wrapper(mock_sock)

        # Ensure connection is set as non-blocking
        mock_conn.setblocking.assert_called_with(False)
        
        # Ensure selector registers the connection
        mock_selector.register.assert_called()

    @patch("server.sel")
    @patch("server.parse_request")
    @patch("server.send_response")
    def test_service_connection(self, mock_send_response, mock_parse_request, mock_selector):
        """Test handling of a service connection."""
        mock_sock = MagicMock()
        mock_data = types.SimpleNamespace(addr=("127.0.0.1", 50000), inb=b"", outb=b"")
        key = selectors.SelectorKey(fileobj=mock_sock, fd=1, events=selectors.EVENT_READ, data=mock_data)

        mock_sock.recv.return_value = b'{"task": "list-accounts", "wildcard": "*"}'
        mock_parse_request.return_value = {"task": "list-accounts", "wildcard": "*"}

        service_connection(key, selectors.EVENT_READ)

        # Ensure request parsing was called
        mock_parse_request.assert_called()
        # Ensure response was sent back
        mock_send_response.assert_called()

    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_write_users_messages_json(self, mock_open):
        """Test saving users and messages to JSON files."""
        users_dict = {
            "user1": User(uid="user1", username="testuser", password="hashedpass")
        }
        messages_dict = {
            "msg1": Message(mid="msg1", sender="user1", receiver="user2", sender_username="user1", receiver_username="user2", text="Hello", timestamp="2024-02-11T12:34:56")
        }

        write_users_messages_json(users_dict, messages_dict)

        # Ensure both user.json and message.json were written to
        mock_open.assert_any_call("server/test/user.json", "w")
        mock_open.assert_any_call("server/test/message.json", "w")

        # Check file writes contain correct data
        mock_open().write.assert_called()

if __name__ == "__main__":
    unittest.main()
