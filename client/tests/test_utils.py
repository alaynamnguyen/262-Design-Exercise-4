import pytest
import json
import hashlib
import sys 
import os
from unittest.mock import Mock, patch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import hash_password

# ---------------- TESTS FOR PASSWORD HASHING ---------------- #

@pytest.mark.parametrize("password", ["password123", "securePass!", "admin"])
def test_hash_password(password):
    """
    Test if hash_password() correctly hashes passwords using SHA-256.
    """
    hashed_value = hash_password(password)
    expected_value = hashlib.sha256(password.encode()).hexdigest()

    assert hashed_value == expected_value
    assert len(hashed_value) == 64  # SHA-256 produces 64-character hex strings
