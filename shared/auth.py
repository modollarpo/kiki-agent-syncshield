"""
Authentication Utilities for KIKI Agent™

Provides JWT token generation/validation, password hashing, and OAuth2 utilities.
Designed for production use with secure defaults.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

# ============================================================================
# Configuration
# ============================================================================

# JWT Configuration
SECRET_KEY = os.getenv("KIKI_JWT_SECRET", "CHANGE_THIS_IN_PRODUCTION_OR_USE_ENV_VAR")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("KIKI_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("KIKI_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password Configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================================================
# Password Utilities
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
        
    Example:
        hashed = hash_password("my_secure_password")
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password from user
        hashed_password: Stored hashed password
        
    Returns:
        True if password matches, False otherwise
        
    Example:
        if verify_password(input_password, stored_hash):
            # Password correct
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# JWT Token Utilities
# ============================================================================

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload to encode (typically user_id, email, roles)
        expires_delta: Token expiration time (default: 30 minutes)
        
    Returns:
        Encoded JWT token string
        
    Example:
        token = create_access_token({"sub": user.email, "user_id": user.user_id})
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: Payload to encode (typically user_id, email)
        expires_delta: Token expiration time (default: 7 days)
        
    Returns:
        Encoded JWT refresh token string
        
    Example:
        refresh = create_refresh_token({"sub": user.email, "user_id": user.user_id})
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
        
    Example:
        try:
            payload = decode_token(token)
            user_id = payload.get("user_id")
        except HTTPException:
            # Token invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    Verify token is valid and of correct type.
    
    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid, expired, or wrong type
        
    Example:
        payload = verify_token(access_token, "access")
    """
    payload = decode_token(token)
    
    # Verify token type
    if payload.get("type") != token_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type. Expected {token_type}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


# ============================================================================
# API Key Utilities (for service-to-service auth)
# ============================================================================

def generate_api_key() -> str:
    """
    Generate a secure random API key.
    
    Returns:
        Random API key string (32 bytes, hex encoded)
        
    Example:
        key = generate_api_key()
        # Store hashed version: hash_password(key)
    """
    import secrets
    return secrets.token_hex(32)


def validate_api_key(api_key: str, hashed_key: str) -> bool:
    """
    Validate an API key against its hash.
    
    Args:
        api_key: Plain API key from request
        hashed_key: Stored hashed API key
        
    Returns:
        True if API key matches, False otherwise
        
    Example:
        if validate_api_key(request_key, stored_hash):
            # API key valid
    """
    return verify_password(api_key, hashed_key)


# ============================================================================
# Security Checks
# ============================================================================

def check_production_security():
    """
    Check if production security settings are configured.
    
    Raises:
        RuntimeError: If using default secret key in production
        
    Example:
        # Call at application startup
        check_production_security()
    """
    if SECRET_KEY == "CHANGE_THIS_IN_PRODUCTION_OR_USE_ENV_VAR":
        if os.getenv("KIKI_ENV", "development") == "production":
            raise RuntimeError(
                "CRITICAL: Using default JWT secret in production! "
                "Set KIKI_JWT_SECRET environment variable."
            )
