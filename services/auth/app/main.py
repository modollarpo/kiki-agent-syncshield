"""
Authentication API for KIKI Agent™

Provides user registration, login, token management, and API key generation.
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import uuid
import logging
import secrets

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
    APIKeyResponse,
    InviteCodeGenerateRequest,
    InviteCodeResponse,
    InviteCodeListResponse
)
from shared.models import UserModel, AuditLogModel, InviteCodeModel
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
    Register a new user with invite code (invite-only registration).
    
    - **username**: Unique username (3-50 characters)
    - **email**: Valid email address
    - **password**: Secure password (min 8 chars, upper, lower, digit)
    - **invite_code**: Valid invite code (required for registration)
    - **full_name**: Optional full name
    - **organization_name**: Optional organization name
    """
    # Validate invite code
    invite = db.query(InviteCodeModel).filter(
        InviteCodeModel.code == user_data.invite_code
    ).first()
    
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid invite code"
        )
    
    if invite.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite code has already been used"
        )
    
    if invite.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite code has been revoked"
        )
    
    if invite.expires_at and invite.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite code has expired"
        )
    
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
    db.flush()  # Flush to get user.id before marking invite as used
    
    # Mark invite as used
    invite.is_used = True
    invite.used_by_id = user.id
    invite.used_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    # Audit log
    audit = AuditLogModel(
        event_type="user.registered",
        event_data={
            "user_id": user.user_id,
            "username": user.username,
            "invite_code": user_data.invite_code
        },
        user_id=user.user_id
    )
    db.add(audit)
    db.commit()
    
    logger.info(f"User registered: {user.username} ({user.user_id}) with invite {invite.code}")
    
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
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    admin: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    List all users (admin only).
    
    Args:
        skip: Pagination offset
        limit: Max results
        role: Filter by role (user, admin)
        is_active: Filter by active status
    """
    query = db.query(UserModel)
    
    if role:
        query = query.filter(UserModel.role == role)
    if is_active is not None:
        query = query.filter(UserModel.is_active == is_active)
    
    users = query.order_by(UserModel.created_at.desc()).offset(skip).limit(limit).all()
    return users


@app.post("/api/auth/users/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def admin_create_user(
    user_data: UserRegisterRequest,
    role: str = "user",
    admin: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create new user (admin only).
    
    Args:
        user_data: User registration data
        role: User role (user or admin)
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
    
    # Validate role
    if role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'user' or 'admin'"
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
        role=role,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Audit log
    audit = AuditLogModel(
        event_type="user.created_by_admin",
        event_data={
            "created_user_id": user.user_id,
            "username": user.username,
            "role": role,
            "created_by": admin.user_id
        },
        user_id=admin.user_id
    )
    db.add(audit)
    db.commit()
    
    logger.info(f"User created by admin: {user.username} ({role}) by {admin.username}")
    
    return user


@app.patch("/api/auth/users/{user_id}/role")
def update_user_role(
    user_id: str,
    new_role: str,
    admin: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update user role (admin only).
    
    Args:
        user_id: User ID to update
        new_role: New role (user or admin)
    """
    if new_role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'user' or 'admin'"
        )
    
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    old_role = user.role
    user.role = new_role
    db.commit()
    
    # Audit log
    audit = AuditLogModel(
        event_type="user.role_updated",
        event_data={
            "user_id": user_id,
            "old_role": old_role,
            "new_role": new_role,
            "updated_by": admin.user_id
        },
        user_id=admin.user_id
    )
    db.add(audit)
    db.commit()
    
    logger.info(f"User role updated: {user.username} {old_role} → {new_role} by {admin.username}")
    
    return {"message": f"User role updated to {new_role}", "user_id": user_id, "new_role": new_role}


@app.patch("/api/auth/users/{user_id}/activate")
def activate_user(
    user_id: str,
    active: bool,
    admin: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Activate or deactivate user (admin only).
    
    Args:
        user_id: User ID to update
        active: True to activate, False to deactivate
    """
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = active
    db.commit()
    
    # Audit log
    audit = AuditLogModel(
        event_type="user.activated" if active else "user.deactivated",
        event_data={
            "user_id": user_id,
            "username": user.username,
            "updated_by": admin.user_id
        },
        user_id=admin.user_id
    )
    db.add(audit)
    db.commit()
    
    action = "activated" if active else "deactivated"
    logger.info(f"User {action}: {user.username} by {admin.username}")
    
    return {"message": f"User {action} successfully", "user_id": user_id, "is_active": active}


@app.delete("/api/auth/users/{user_id}")
def delete_user(
    user_id: str,
    admin: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete user (admin only). Performs soft delete by deactivating.
    """
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent self-deletion
    if user.user_id == admin.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
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
# Invite Code Management (Admin Only)
# ============================================================================

@app.post("/api/auth/invites/generate", response_model=InviteCodeListResponse)
def generate_invite_codes(
    request: InviteCodeGenerateRequest,
    admin: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Generate new invite codes (admin only).
    
    Args:
        request: Number of codes to generate and optional expiration
    
    Returns:
        List of generated invite codes
    """
    codes = []
    expires_at = None
    
    if request.expires_days:
        expires_at = datetime.utcnow() + timedelta(days=request.expires_days)
    
    for _ in range(request.count):
        # Generate secure random code
        code = f"KIKI-{secrets.token_urlsafe(16)[:16]}"
        
        invite = InviteCodeModel(
            code=code,
            created_by_id=admin.id,
            expires_at=expires_at
        )
        
        db.add(invite)
        codes.append(invite)
    
    db.commit()
    
    # Refresh all codes to get database-generated fields
    for invite in codes:
        db.refresh(invite)
    
    # Audit log
    audit = AuditLogModel(
        event_type="invites.generated",
        event_data={
            "count": request.count,
            "expires_days": request.expires_days,
            "generated_by": admin.user_id
        },
        user_id=admin.user_id
    )
    db.add(audit)
    db.commit()
    
    logger.info(f"Generated {request.count} invite codes by {admin.username}")
    
    # Build response with metadata
    responses = []
    for invite in codes:
        responses.append(InviteCodeResponse(
            id=invite.id,
            code=invite.code,
            created_by_id=invite.created_by_id,
            used_by_id=invite.used_by_id,
            is_used=invite.is_used,
            is_revoked=invite.is_revoked,
            created_at=invite.created_at,
            used_at=invite.used_at,
            expires_at=invite.expires_at,
            created_by_email=admin.email
        ))
    
    return InviteCodeListResponse(
        total=len(responses),
        unused=len(responses),
        used=0,
        revoked=0,
        codes=responses
    )


@app.get("/api/auth/invites", response_model=InviteCodeListResponse)
def list_invite_codes(
    status_filter: str = Query("all", description="Filter by status: all, unused, used, revoked"),
    admin: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    List all invite codes (admin only).
    
    Args:
        status_filter: Filter by status (all, unused, used, revoked)
    
    Returns:
        List of invite codes with statistics
    """
    query = db.query(InviteCodeModel)
    
    if status_filter == "unused":
        query = query.filter(
            and_(
                InviteCodeModel.is_used == False,
                InviteCodeModel.is_revoked == False
            )
        )
    elif status_filter == "used":
        query = query.filter(InviteCodeModel.is_used == True)
    elif status_filter == "revoked":
        query = query.filter(InviteCodeModel.is_revoked == True)
    
    invites = query.order_by(InviteCodeModel.created_at.desc()).all()
    
    # Calculate statistics
    all_invites = db.query(InviteCodeModel).all()
    total = len(all_invites)
    unused = len([i for i in all_invites if not i.is_used and not i.is_revoked])
    used = len([i for i in all_invites if i.is_used])
    revoked = len([i for i in all_invites if i.is_revoked])
    
    # Build responses with creator and user emails
    responses = []
    for invite in invites:
        creator = db.query(UserModel).filter(UserModel.id == invite.created_by_id).first()
        user = None
        if invite.used_by_id:
            user = db.query(UserModel).filter(UserModel.id == invite.used_by_id).first()
        
        responses.append(InviteCodeResponse(
            id=invite.id,
            code=invite.code,
            created_by_id=invite.created_by_id,
            used_by_id=invite.used_by_id,
            is_used=invite.is_used,
            is_revoked=invite.is_revoked,
            created_at=invite.created_at,
            used_at=invite.used_at,
            expires_at=invite.expires_at,
            created_by_email=creator.email if creator else None,
            used_by_email=user.email if user else None
        ))
    
    return InviteCodeListResponse(
        total=total,
        unused=unused,
        used=used,
        revoked=revoked,
        codes=responses
    )


@app.delete("/api/auth/invites/{code}")
def revoke_invite_code(
    code: str,
    admin: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Revoke an unused invite code (admin only).
    
    Args:
        code: Invite code to revoke
    
    Returns:
        Success message
    """
    invite = db.query(InviteCodeModel).filter(InviteCodeModel.code == code).first()
    
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite code not found"
        )
    
    if invite.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot revoke used invite code"
        )
    
    if invite.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite code already revoked"
        )
    
    invite.is_revoked = True
    db.commit()
    
    # Audit log
    audit = AuditLogModel(
        event_type="invite.revoked",
        event_data={
            "code": code,
            "revoked_by": admin.user_id
        },
        user_id=admin.user_id
    )
    db.add(audit)
    db.commit()
    
    logger.info(f"Invite code revoked: {code} by {admin.username}")
    
    return {"message": "Invite code revoked successfully", "code": code}


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
