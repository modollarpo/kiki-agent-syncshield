"""
Field-Level Encryption for KIKI Agent™

Encrypts sensitive fields (API keys, tokens, PII) in database.
Uses AES-256-GCM for authenticated encryption with Fernet wrapper.
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ============================================================================
# Encryption Key Management
# ============================================================================

def get_encryption_key() -> bytes:
    """
    Get or generate encryption key from environment.
    
    Key is derived from KIKI_ENCRYPTION_KEY environment variable using PBKDF2.
    Falls back to a default key in development (INSECURE).
    
    Returns:
        32-byte encryption key
        
    Raises:
        RuntimeError: If using default key in production
    """
    # Get master key from environment
    master_key = os.getenv("KIKI_ENCRYPTION_KEY", "CHANGE_THIS_IN_PRODUCTION")
    
    # Check production security
    if master_key == "CHANGE_THIS_IN_PRODUCTION":
        if os.getenv("KIKI_ENV", "development") == "production":
            raise RuntimeError(
                "CRITICAL: Using default encryption key in production! "
                "Set KIKI_ENCRYPTION_KEY environment variable."
            )
        logger.warning("Using default encryption key - ONLY USE IN DEVELOPMENT")
    
    # Derive key using PBKDF2
    # Use a fixed salt for deterministic key derivation
    # In production, could use per-field salts stored alongside encrypted data
    salt = b"kiki_encryption_salt_v1"
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
    return key


# Initialize Fernet cipher
_fernet: Optional[Fernet] = None

def get_cipher() -> Fernet:
    """
    Get initialized Fernet cipher (singleton pattern).
    
    Returns:
        Fernet cipher instance
    """
    global _fernet
    if _fernet is None:
        key = get_encryption_key()
        _fernet = Fernet(key)
    return _fernet


# ============================================================================
# Encryption/Decryption
# ============================================================================

def encrypt(plaintext: str) -> str:
    """
    Encrypt plaintext string.
    
    Uses AES-256-GCM via Fernet. Result includes:
    - Timestamp (8 bytes)
    - IV (16 bytes)
    - Ciphertext (variable)
    - HMAC tag (16 bytes)
    
    Args:
        plaintext: String to encrypt (API key, token, PII, etc.)
        
    Returns:
        Base64-encoded encrypted string
        
    Example:
        encrypted_key = encrypt("sk_live_abc123...")
        # Store encrypted_key in database
    """
    if not plaintext:
        return ""
    
    cipher = get_cipher()
    encrypted_bytes = cipher.encrypt(plaintext.encode('utf-8'))
    return encrypted_bytes.decode('utf-8')


def decrypt(ciphertext: str) -> str:
    """
    Decrypt ciphertext string.
    
    Args:
        ciphertext: Base64-encoded encrypted string from encrypt()
        
    Returns:
        Decrypted plaintext string
        
    Raises:
        cryptography.fernet.InvalidToken: If ciphertext is corrupted or key is wrong
        
    Example:
        decrypted_key = decrypt(stored_encrypted_key)
        # Use decrypted_key for API calls
    """
    if not ciphertext:
        return ""
    
    cipher = get_cipher()
    decrypted_bytes = cipher.decrypt(ciphertext.encode('utf-8'))
    return decrypted_bytes.decode('utf-8')


# ============================================================================
# Database Field Encryption Helpers
# ============================================================================

def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt API key for database storage.
    
    Args:
        api_key: Plaintext API key
        
    Returns:
        Encrypted API key (safe to store in database)
    """
    return encrypt(api_key)


def decrypt_api_key(encrypted_api_key: str) -> str:
    """
    Decrypt API key from database.
    
    Args:
        encrypted_api_key: Encrypted API key from database
        
    Returns:
        Plaintext API key (for API calls)
    """
    return decrypt(encrypted_api_key)


def encrypt_email(email: str) -> str:
    """
    Encrypt email for GDPR compliance.
    
    Args:
        email: Plaintext email address
        
    Returns:
        Encrypted email
    """
    return encrypt(email.lower())


def decrypt_email(encrypted_email: str) -> str:
    """
    Decrypt email from database.
    
    Args:
        encrypted_email: Encrypted email from database
        
    Returns:
        Plaintext email
    """
    return decrypt(encrypted_email)


# ============================================================================
# SQLAlchemy Integration
# ============================================================================

from sqlalchemy.types import TypeDecorator, String

class EncryptedString(TypeDecorator):
    """
    SQLAlchemy column type for automatic encryption/decryption.
    
    Usage:
        class User(Base):
            __tablename__ = "users"
            api_key = Column(EncryptedString(500), nullable=True)
    
    The field will be automatically encrypted when written to database
    and decrypted when read from database.
    """
    impl = String
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        """Encrypt value before storing in database"""
        if value is not None:
            return encrypt(value)
        return value
    
    def process_result_value(self, value, dialect):
        """Decrypt value after reading from database"""
        if value is not None:
            return decrypt(value)
        return value


# ============================================================================
# Key Rotation
# ============================================================================

def rotate_encryption_key(old_key: str, new_key: str, ciphertext: str) -> str:
    """
    Rotate encryption key for a single encrypted value.
    
    Process:
    1. Decrypt with old key
    2. Re-encrypt with new key
    
    Args:
        old_key: Previous encryption key
        new_key: New encryption key
        ciphertext: Encrypted value to re-encrypt
        
    Returns:
        Ciphertext encrypted with new key
        
    Example:
        # In migration script
        for user in db.query(User).all():
            user.api_key = rotate_encryption_key(
                old_key=os.getenv("OLD_ENCRYPTION_KEY"),
                new_key=os.getenv("KIKI_ENCRYPTION_KEY"),
                ciphertext=user.api_key
            )
        db.commit()
    """
    # Create ciphers for old and new keys
    old_kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"kiki_encryption_salt_v1",
        iterations=100000,
        backend=default_backend()
    )
    old_cipher_key = base64.urlsafe_b64encode(old_kdf.derive(old_key.encode()))
    old_cipher = Fernet(old_cipher_key)
    
    new_kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"kiki_encryption_salt_v1",
        iterations=100000,
        backend=default_backend()
    )
    new_cipher_key = base64.urlsafe_b64encode(new_kdf.derive(new_key.encode()))
    new_cipher = Fernet(new_cipher_key)
    
    # Decrypt with old key
    plaintext = old_cipher.decrypt(ciphertext.encode('utf-8'))
    
    # Encrypt with new key
    new_ciphertext = new_cipher.encrypt(plaintext)
    
    return new_ciphertext.decode('utf-8')


# ============================================================================
# Security Checks
# ============================================================================

def check_encryption_security():
    """
    Check if encryption is properly configured.
    
    Raises:
        RuntimeError: If using default encryption key in production
        
    Example:
        # Call at application startup
        check_encryption_security()
    """
    master_key = os.getenv("KIKI_ENCRYPTION_KEY", "CHANGE_THIS_IN_PRODUCTION")
    
    if master_key == "CHANGE_THIS_IN_PRODUCTION":
        if os.getenv("KIKI_ENV", "development") == "production":
            raise RuntimeError(
                "CRITICAL: Using default encryption key in production! "
                "Set KIKI_ENCRYPTION_KEY environment variable."
            )


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    # Test encryption/decryption
    test_api_key = "sk_live_abc123def456ghi789"
    
    print("Testing field-level encryption...")
    print(f"Original: {test_api_key}")
    
    encrypted = encrypt_api_key(test_api_key)
    print(f"Encrypted: {encrypted}")
    
    decrypted = decrypt_api_key(encrypted)
    print(f"Decrypted: {decrypted}")
    
    assert test_api_key == decrypted, "Encryption/decryption failed!"
    print("✓ Encryption test passed")
