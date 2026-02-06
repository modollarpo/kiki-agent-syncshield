"""Create initial super admin account

Revision ID: 6b1424f7a091
Revises: 834c458d1fc5
Create Date: 2026-02-06 15:38:05.467449+00:00

Creates an initial super-admin account from environment variables:
- KIKI_ADMIN_EMAIL (required)
- KIKI_ADMIN_PASSWORD (required)
- KIKI_ADMIN_USERNAME (optional, defaults to "admin")
- KIKI_ADMIN_FULLNAME (optional, defaults to "KIKI Administrator")

If credentials are not provided, migration will skip admin creation.
You can create admin later using scripts/promote_admin.py

Usage:
    export KIKI_ADMIN_EMAIL="admin@kiki.ai"
    export KIKI_ADMIN_PASSWORD="YourSecurePassword123"
    alembic upgrade head
"""
from typing import Sequence, Union
import os
import uuid
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision: str = '6b1424f7a091'
down_revision: Union[str, None] = '834c458d1fc5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial super-admin account if environment variables are set"""
    
    # Get admin credentials from environment
    admin_email = os.getenv("KIKI_ADMIN_EMAIL")
    admin_password = os.getenv("KIKI_ADMIN_PASSWORD")
    admin_username = os.getenv("KIKI_ADMIN_USERNAME", "admin")
    
    # Skip if credentials not provided
    if not admin_email or not admin_password:
        print("ℹ️  Skipping admin creation - KIKI_ADMIN_EMAIL or KIKI_ADMIN_PASSWORD not set")
        print("   You can create admin later using: python scripts/promote_admin.py")
        return
    
    # Truncate password to 72 bytes for bcrypt compatibility
    password_bytes = admin_password.encode('utf-8')[:72]
    
    # Hash password using bcrypt directly
    import bcrypt
    password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
    
    # Generate user ID
    user_id = f"usr_{uuid.uuid4().hex[:12]}"
    
    # Get database connection
    bind = op.get_bind()
    session = Session(bind=bind)
    
    # Check if admin already exists
    result = session.execute(
        sa.text("SELECT user_id FROM users WHERE email = :email"),
        {"email": admin_email}
    ).fetchone()
    
    if result:
        print(f"ℹ️  Admin user already exists: {admin_email}")
        return
    
    # Insert admin user (matching actual users table schema)
    session.execute(
        sa.text("""
            INSERT INTO users (
                user_id, username, email, password_hash, role, created_at, last_login_at
            ) VALUES (
                :user_id, :username, :email, :password_hash, :role, :created_at, :last_login_at
            )
        """),
        {
            "user_id": user_id,
            "username": admin_username,
            "email": admin_email,
            "password_hash": password_hash,
            "role": "admin",
            "created_at": datetime.utcnow(),
            "last_login_at": None
        }
    )
    
    session.commit()
    
    print("=" * 60)
    print("✅ Initial super-admin account created successfully!")
    print("=" * 60)
    print(f"   Username: {admin_username}")
    print(f"   Email: {admin_email}")
    print(f"   User ID: {user_id}")
    print("=" * 60)
    print("⚠️  IMPORTANT: Delete KIKI_ADMIN_PASSWORD from environment after first login!")
    print("=" * 60)


def downgrade() -> None:
    """Remove admin account created by this migration"""
    
    admin_email = os.getenv("KIKI_ADMIN_EMAIL")
    
    if not admin_email:
        print("ℹ️  No admin email specified, skipping downgrade")
        return
    
    bind = op.get_bind()
    session = Session(bind=bind)
    
    # Delete admin user
    result = session.execute(
        sa.text("DELETE FROM users WHERE email = :email"),
        {"email": admin_email}
    )
    
    session.commit()
    
    if result.rowcount > 0:
        print(f"✅ Removed admin user: {admin_email}")
    else:
        print(f"ℹ️  Admin user not found: {admin_email}")

