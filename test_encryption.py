#!/usr/bin/env python3
"""Test encryption functionality"""

import sys
import os

# Add parent directory to path to avoid types/ conflict
sys.path.insert(0, '/workspaces/kiki-agent-syncshield')

# Now import after path is set
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

# Simplified encryption test
def test_encryption():
    # Generate key
    master_key = "test_master_key_for_encryption"
    salt = b"kiki_encryption_salt_v1"
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
    cipher = Fernet(key)
    
    # Test encryption/decryption
    test_api_key = "sk_live_test_api_key_12345"
    print(f"Original: {test_api_key}")
    
    encrypted = cipher.encrypt(test_api_key.encode('utf-8'))
    print(f"Encrypted: {encrypted.decode('utf-8')[:50]}...")
    
    decrypted = cipher.decrypt(encrypted).decode('utf-8')
    print(f"Decrypted: {decrypted}")
    
    assert test_api_key == decrypted, "Encryption test failed!"
    print("✓ Encryption test passed")

if __name__ == "__main__":
    test_encryption()
