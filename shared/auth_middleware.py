"""
Authentication Middleware and Dependencies for KIKI Agent™

FastAPI dependencies for protecting endpoints with OAuth2/JWT authentication.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from shared.auth import verify_token, validate_api_key
from shared.models import UserModel
from services.syncvalue.database import get_db

# ============================================================================
# OAuth2 Configuration
# ============================================================================

# OAuth2 password flow (for user authentication)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=True
)

# HTTP Bearer (for API key authentication)
http_bearer = HTTPBearer(auto_error=False)

# ============================================================================
# User Authentication Dependencies
# ============================================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserModel:
    """
    Get current authenticated user from JWT token.
    
    Args:
        token: JWT access token from Authorization header
        db: Database session
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token invalid or user not found
        
    Example:
        @app.get("/me")
        def get_me(user: UserModel = Depends(get_current_user)):
            return user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        payload = verify_token(token, "access")
        user_id: str = payload.get("user_id")
        
        if user_id is None:
            raise credentials_exception
            
    except Exception:
        raise credentials_exception
    
    # Get user from database
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user


async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    """
    Get current active user (additional check for account status).
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If user account is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    """
    Get current user and verify admin role.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        Current admin user
        
    Raises:
        HTTPException: If user is not an admin
        
    Example:
        @app.delete("/users/{user_id}")
        def delete_user(user_id: str, admin: UserModel = Depends(get_current_admin_user)):
            # Only admins can access this
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# ============================================================================
# Optional Authentication (for public/private dual endpoints)
# ============================================================================

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    db: Session = Depends(get_db)
) -> Optional[UserModel]:
    """
    Get user if authenticated, None otherwise.
    
    Useful for endpoints that work differently for authenticated vs anonymous users.
    
    Args:
        credentials: Optional bearer token
        db: Database session
        
    Returns:
        User if authenticated, None otherwise
        
    Example:
        @app.get("/campaigns")
        def list_campaigns(user: Optional[UserModel] = Depends(get_optional_user)):
            if user:
                # Show user's campaigns
                return get_user_campaigns(user.user_id)
            else:
                # Show public campaigns only
                return get_public_campaigns()
    """
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials, "access")
        user_id = payload.get("user_id")
        
        if user_id:
            user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
            return user if user and user.is_active else None
            
    except Exception:
        pass
    
    return None


# ============================================================================
# Service-to-Service Authentication (API Keys)
# ============================================================================

async def verify_service_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: Session = Depends(get_db)
) -> str:
    """
    Verify service API key for inter-service communication.
    
    Args:
        credentials: Bearer token (API key)
        db: Database session
        
    Returns:
        Service name/ID
        
    Raises:
        HTTPException: If API key is invalid
        
    Example:
        @app.post("/internal/syncflow/bid")
        def process_bid(
            bid_data: dict,
            service: str = Depends(verify_service_api_key)
        ):
            # Only authorized services can access
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key = credentials.credentials
    
    # TODO: Implement API key storage in database
    # For now, check against environment variable
    valid_api_keys = {
        os.getenv("SYNCFLOW_API_KEY"): "syncflow",
        os.getenv("SYNCBRAIN_API_KEY"): "syncbrain",
        os.getenv("SYNCCREATE_API_KEY"): "synccreate",
        os.getenv("SYNCSHIELD_API_KEY"): "syncshield",
    }
    
    for stored_key, service_name in valid_api_keys.items():
        if stored_key and api_key == stored_key:
            return service_name
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
        headers={"WWW-Authenticate": "Bearer"},
    )


# ============================================================================
# Organization Access Control
# ============================================================================

def verify_organization_access(
    organization_id: str,
    user: UserModel
) -> bool:
    """
    Verify user has access to organization.
    
    Args:
        organization_id: Organization to check access for
        user: Current user
        
    Returns:
        True if user has access, False otherwise
        
    Example:
        if not verify_organization_access(campaign.organization_id, current_user):
            raise HTTPException(403, "Access denied")
    """
    # Admin has access to all organizations
    if user.role == "admin":
        return True
    
    # User must belong to the organization
    return user.organization_id == organization_id
