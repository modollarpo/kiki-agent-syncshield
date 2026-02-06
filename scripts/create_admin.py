#!/usr/bin/env python3
"""
KIKI Agent™ - Create Initial Admin User

This script creates the first admin user or promotes an existing user to admin.

Usage:
    python scripts/create_admin.py --email admin@example.com --password SecurePass123
    python scripts/create_admin.py --promote user@example.com
"""

import sys
import os
import argparse
from datetime import datetime
import uuid

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.auth import hash_password
from shared.database import UserModel


def get_db_session():
    """Create database session"""
    database_url = os.getenv("DATABASE_URL", "postgresql://kiki_user:kiki_pass@localhost:5432/kiki_db")
    
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def create_admin_user(email: str, password: str, username: str = None, full_name: str = None):
    """
    Create new admin user
    
    Args:
        email: Admin email
        password: Admin password
        username: Admin username (defaults to email)
        full_name: Admin full name
    """
    db = get_db_session()
    
    try:
        # Check if email already exists
        existing = db.query(UserModel).filter(UserModel.email == email).first()
        if existing:
            print(f"❌ Error: User with email {email} already exists")
            print(f"   Use --promote {email} to promote existing user to admin")
            return False
        
        # Use email as username if not provided
        if not username:
            username = email.split('@')[0]
        
        # Check if username exists
        existing_username = db.query(UserModel).filter(UserModel.username == username).first()
        if existing_username:
            username = f"{username}_{uuid.uuid4().hex[:4]}"
            print(f"⚠️  Username taken, using: {username}")
        
        # Create admin user
        admin = UserModel(
            user_id=f"usr_{uuid.uuid4().hex[:12]}",
            username=username,
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name or "Administrator",
            role="admin",
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("✅ Admin user created successfully!")
        print(f"   User ID: {admin.user_id}")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Role: {admin.role}")
        print(f"\n🔐 Login credentials:")
        print(f"   Email/Username: {email}")
        print(f"   Password: {password}")
        print(f"\n🌐 Login at: http://localhost:8021/login")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def promote_user_to_admin(email: str):
    """
    Promote existing user to admin role
    
    Args:
        email: User email to promote
    """
    db = get_db_session()
    
    try:
        # Find user by email
        user = db.query(UserModel).filter(UserModel.email == email).first()
        
        if not user:
            print(f"❌ Error: User with email {email} not found")
            return False
        
        if user.role == "admin":
            print(f"⚠️  User {email} is already an admin")
            return True
        
        # Update role
        old_role = user.role
        user.role = "admin"
        db.commit()
        
        print(f"✅ User promoted to admin successfully!")
        print(f"   User ID: {user.user_id}")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Role: {old_role} → {user.role}")
        print(f"\n🌐 User can now access admin features at: http://localhost:8021/admin/users")
        
        return True
        
    except Exception as e:
        print(f"❌ Error promoting user: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Create admin user or promote existing user to admin",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create new admin user
  python scripts/create_admin.py --email admin@kiki.ai --password SecurePass123

  # Create with custom username
  python scripts/create_admin.py --email admin@kiki.ai --password SecurePass123 --username admin

  # Promote existing user to admin
  python scripts/create_admin.py --promote user@example.com

Environment Variables:
  DATABASE_URL    PostgreSQL connection string (default: postgresql://kiki_user:kiki_pass@localhost:5432/kiki_db)
        """
    )
    
    parser.add_argument("--email", help="Admin email address")
    parser.add_argument("--password", help="Admin password (minimum 8 characters)")
    parser.add_argument("--username", help="Admin username (optional, defaults to email prefix)")
    parser.add_argument("--full-name", help="Admin full name (optional)")
    parser.add_argument("--promote", help="Promote existing user to admin by email")
    
    args = parser.parse_args()
    
    # Promote existing user
    if args.promote:
        success = promote_user_to_admin(args.promote)
        sys.exit(0 if success else 1)
    
    # Create new admin user
    if not args.email or not args.password:
        parser.print_help()
        print("\n❌ Error: --email and --password are required (or use --promote)")
        sys.exit(1)
    
    if len(args.password) < 8:
        print("❌ Error: Password must be at least 8 characters")
        sys.exit(1)
    
    success = create_admin_user(
        email=args.email,
        password=args.password,
        username=args.username,
        full_name=args.full_name
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
