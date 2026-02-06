"""
Pydantic Models for Authentication

Request/response schemas for authentication endpoints.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserRegisterRequest(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    invite_code: str = Field(..., min_length=1, description="Valid invite code (required)")
    full_name: Optional[str] = Field(None, max_length=200, description="User's full name")
    organization_name: Optional[str] = Field(None, max_length=200, description="Organization name")
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "SecurePass123",
                "invite_code": "KIKI-abc123def456",
                "full_name": "John Doe",
                "organization_name": "Acme Corp"
            }
        }


class UserLoginRequest(BaseModel):
    """User login request (OAuth2 password flow)"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "password": "SecurePass123"
            }
        }


class TokenResponse(BaseModel):
    """Authentication token response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user_id: str = Field(..., description="User ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user_id": "usr_abc123"
            }
        }


class TokenRefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str = Field(..., description="JWT refresh token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
            }
        }


class UserResponse(BaseModel):
    """User information response"""
    user_id: str
    username: str
    email: str
    full_name: Optional[str]
    role: str
    organization_id: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_id": "usr_abc123",
                "username": "johndoe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "role": "user",
                "organization_id": "org_xyz789",
                "is_active": True,
                "created_at": "2026-02-06T14:30:00Z"
            }
        }


class PasswordChangeRequest(BaseModel):
    """Password change request"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")
    
    @validator('new_password')
    def password_strength(cls, v):
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "OldPass123",
                "new_password": "NewSecurePass456"
            }
        }


class APIKeyCreateRequest(BaseModel):
    """API key creation request"""
    name: str = Field(..., min_length=1, max_length=100, description="Key name/description")
    expires_days: Optional[int] = Field(None, ge=1, le=365, description="Expiration in days")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Production API Key",
                "expires_days": 90
            }
        }


class APIKeyResponse(BaseModel):
    """API key response"""
    key_id: str
    name: str
    api_key: Optional[str] = None  # Only returned on creation
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "key_id": "key_abc123",
                "name": "Production API Key",
                "api_key": "sk_live_abc123...",
                "created_at": "2026-02-06T14:30:00Z",
                "expires_at": "2026-05-06T14:30:00Z",
                "last_used_at": None
            }
        }


# ============================================================================
# Invite Code Schemas
# ============================================================================

class InviteCodeGenerateRequest(BaseModel):
    """Request to generate new invite codes"""
    count: int = Field(default=1, ge=1, le=100, description="Number of invite codes to generate")
    expires_days: Optional[int] = Field(None, ge=1, le=365, description="Expiration in days (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "count": 5,
                "expires_days": 30
            }
        }


class InviteCodeResponse(BaseModel):
    """Invite code information response"""
    id: int
    code: str
    created_by_id: int
    used_by_id: Optional[int]
    is_used: bool
    is_revoked: bool
    created_at: datetime
    used_at: Optional[datetime]
    expires_at: Optional[datetime]
    
    # Extra fields for convenience
    created_by_email: Optional[str] = None
    used_by_email: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "code": "KIKI-a1b2c3d4e5f6",
                "created_by_id": 1,
                "used_by_id": None,
                "is_used": False,
                "is_revoked": False,
                "created_at": "2026-02-06T14:30:00Z",
                "used_at": None,
                "expires_at": "2026-03-08T14:30:00Z",
                "created_by_email": "admin@kiki.ai",
                "used_by_email": None
            }
        }


class InviteCodeListResponse(BaseModel):
    """List of invite codes with metadata"""
    total: int
    unused: int
    used: int
    revoked: int
    codes: list[InviteCodeResponse]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 10,
                "unused": 5,
                "used": 3,
                "revoked": 2,
                "codes": []
            }
        }
