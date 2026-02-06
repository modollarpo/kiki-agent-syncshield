"""
Authentication API for KIKI Agent™

Provides user registration, login, token management, and API key generation.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import logging

from shared.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    generate_api_key,
    check_production_security,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from shared.auth_middleware import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user
)
from shared.auth_schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    TokenRefreshRequest,
    UserResponse,
    PasswordChangeRequest,
    APIKeyCreateRequest,
    APIKeyResponse
)
from shared.models import UserModel, AuditLogModel
from services.syncvalue.database import get_db, init_db

# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="KIKI Authentication API",
    description="OAuth2/JWT authentication service for KIKI Agent™",
    version="1.0.0"
)

logger = logging.getLogger(__name__)

# Check security configuration on startup
check_production_security()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    logger.info("Authentication API started")


# ============================================================================
# Health Check
# ============================================================================

@app.get("/healthz")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "auth"}


# ============================================================================
# User Registration
# ============================================================================

@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    - **username**: Unique username (3-50 characters)
    - **email**: Valid email address
    - **password**: Secure password (min 8 chars, upper, lower, digit)
    - **full_name**: Optional full name
    - **organization_name**: Optional organization name
    """
    # Check if username exists
    if db.query(UserModel).filter(UserModel.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    if db.query(UserModel).filter(UserModel.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate organization ID if provided
    organization_id = None
    if user_data.organization_name:
        organization_id = f"org_{uuid.uuid4().hex[:12]}"
    
    # Create user
    user = UserModel(
        user_id=f"usr_{uuid.uuid4().hex[:12]}",
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        organization_id=organization_id,
        role="user",
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Audit log
    audit = AuditLogModel(
        event_type="user.registered",
        event_data={"user_id": user.user_id, "username": user.username},
        user_id=user.user_id
    )
    db.add(audit)
    db.commit()
    
    logger.info(f"User registered: {user.username} ({user.user_id})")
    
    return user


# ============================================================================
# User Login
# ============================================================================

@app.post("/api/auth/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with username/email and password.
    
    Returns access token and refresh token.
    """
    # Find user by username or email
    user = db.query(UserModel).filter(
        (UserModel.username == form_data.username) | (UserModel.email == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Create tokens
    token_data = {
        "sub": user.email,
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": user.email, "user_id": user.user_id})
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # Audit log
    audit = AuditLogModel(
        event_type="user.login",
        event_data={"user_id": user.user_id, "username": user.username},
        user_id=user.user_id
    )
    db.add(audit)
    db.commit()
    
    logger.info(f"User logged in: {user.username} ({user.user_id})")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.user_id
    )


# ============================================================================
# Token Refresh
# ============================================================================

@app.post("/api/auth/refresh", response_model=TokenResponse)
def refresh_access_token(
    refresh_data: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Returns new access token and refresh token.
    """
    # Verify refresh token
    payload = verify_token(refresh_data.refresh_token, "refresh")
    user_id = payload.get("user_id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get user
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    token_data = {
        "sub": user.email,
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role
    }
    
    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token({"sub": user.email, "user_id": user.user_id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.user_id
    )


# ============================================================================
# Current User
# ============================================================================

@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: UserModel = Depends(get_current_active_user)):
    """
    Get current authenticated user information.
    
    Requires valid access token in Authorization header.
    """
    return current_user


# ============================================================================
# Password Management
# ============================================================================

@app.post("/api/auth/change-password")
def change_password(
    password_data: PasswordChangeRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change user password.
    
    Requires current password for verification.
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = hash_password(password_data.new_password)
    db.commit()
    
    # Audit log
    audit = AuditLogModel(
        event_type="user.password_changed",
        event_data={"user_id": current_user.user_id},
        user_id=current_user.user_id
    )
    db.add(audit)
    db.commit()
    
    logger.info(f"Password changed: {current_user.username}")
    
    return {"message": "Password changed successfully"}


# ============================================================================
# User Management (Admin Only)
# ============================================================================

@app.get("/api/auth/users", response_model=list[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    admin: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    List all users (admin only).
    """
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users


@app.delete("/api/auth/users/{user_id}")
def delete_user(
    user_id: str,
    admin: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete user (admin only).
    """
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Soft delete (deactivate)
    user.is_active = False
    db.commit()
    
    # Audit log
    audit = AuditLogModel(
        event_type="user.deleted",
        event_data={"deleted_user_id": user_id, "deleted_by": admin.user_id},
        user_id=admin.user_id
    )
    db.add(audit)
    db.commit()
    
    logger.info(f"User deleted: {user.username} by {admin.username}")
    
    return {"message": f"User {user_id} deleted successfully"}


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8030,
        reload=True,
        log_level="info"
    )
