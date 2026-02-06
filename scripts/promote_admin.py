#!/usr/bin/env python3
"""
Promote User to Admin Role

Manually promote an existing user to admin/super-admin role.
Useful for bootstrapping first admin or fixing role issues.

Usage:
    python scripts/promote_admin.py user@example.com
    python scripts/promote_admin.py --username johndoe
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.syncvalue.database import get_db_context
from shared.models import UserModel


def promote_to_admin(email: str = None, username: str = None):
    """
    Promote user to admin role
    
    Args:
        email: User email to promote
        username: User username to promote
    """
    if not email and not username:
        print("❌ Error: Provide either email or username")
        return False
    
    with get_db_context() as db:
        # Find user
        if email:
            user = db.query(UserModel).filter(UserModel.email == email).first()
            search_by = f"email '{email}'"
        else:
            user = db.query(UserModel).filter(UserModel.username == username).first()
            search_by = f"username '{username}'"
        
        if not user:
            print(f"❌ User not found: {search_by}")
            print("\nAvailable users:")
            users = db.query(UserModel).all()
            for u in users:
                print(f"  - {u.username} ({u.email}) - role: {u.role}")
            return False
        
        # Check if already admin
        if user.role == "admin":
            print(f"ℹ️  User '{user.username}' is already an admin")
            return True
        
        # Promote to admin
        old_role = user.role
        user.role = "admin"
        db.commit()
        
        print(f"✅ Successfully promoted '{user.username}' to admin")
        print(f"   Email: {user.email}")
        print(f"   Old role: {old_role}")
        print(f"   New role: {user.role}")
        print(f"   User ID: {user.user_id}")
        
        return True


def list_users():
    """List all users in the database"""
    with get_db_context() as db:
        users = db.query(UserModel).order_by(UserModel.created_at.desc()).all()
        
        if not users:
            print("No users found in database")
            return
        
        print(f"\n{'Username':<20} {'Email':<30} {'Role':<10} {'Active':<8} {'Created':<20}")
        print("-" * 95)
        
        for user in users:
            created = user.created_at.strftime("%Y-%m-%d %H:%M")
            active = "Yes" if user.is_active else "No"
            print(f"{user.username:<20} {user.email:<30} {user.role:<10} {active:<8} {created:<20}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Promote user to admin role",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/promote_admin.py admin@kiki.ai
  python scripts/promote_admin.py --username admin
  python scripts/promote_admin.py --list
        """
    )
    
    parser.add_argument(
        "email",
        nargs="?",
        help="User email to promote (if not using --username)"
    )
    parser.add_argument(
        "--username",
        help="User username to promote (alternative to email)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all users in database"
    )
    
    args = parser.parse_args()
    
    # List users
    if args.list:
        list_users()
        return
    
    # Promote user
    if args.email:
        success = promote_to_admin(email=args.email)
    elif args.username:
        success = promote_to_admin(username=args.username)
    else:
        parser.print_help()
        sys.exit(1)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
