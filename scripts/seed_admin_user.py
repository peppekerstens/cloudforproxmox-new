#!/usr/bin/env python3
"""
Secure admin user seeding script.

Usage:
  python seed_admin_user.py                    # Use .env values
  python seed_admin_user.py admin@test.com     # Override email
  python seed_admin_user.py --help             # Show help

Environment variables (from .env):
  ADMIN_EMAIL      - Email for admin user
  ADMIN_USERNAME   - Username (optional, defaults to email prefix)
  ADMIN_PASSWORD   - Password (will be hashed with bcrypt)
  ADMIN_FIRSTNAME  - First name (optional)
  ADMIN_LASTNAME   - Last name (optional)

WARNING: This script should only be used in development environments.
For production, use secure credential management (Vault, Secrets Manager, etc.)
"""

import os
import sys
import argparse
from datetime import datetime
from sqlalchemy import create_engine, text


def get_password_hash(password: str) -> str:
    """Generate bcrypt hash of password."""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def seed_admin_user(
    email: str = None,
    username: str = None,
    password: str = None,
    first_name: str = None,
    last_name: str = None,
    skip_exists: bool = True
):
    """
    Seed admin user from environment variables.
    """
    # Load from environment if not provided
    email = email or os.getenv("ADMIN_EMAIL", "admin@example.org")
    username = username or os.getenv("ADMIN_USERNAME", email.split("@")[0])
    password = password or os.getenv("ADMIN_PASSWORD", "superadmin")
    first_name = first_name or os.getenv("ADMIN_FIRSTNAME", "Admin")
    last_name = last_name or os.getenv("ADMIN_LASTNAME", "User")
    
    # Get database URL
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://cloudplatform:cloudplatform_dev_password@localhost:5432/cloudplatform"
    )
    
    try:
        # Connect to database
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Check if user exists
            result = conn.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": email}
            )
            user_exists = result.fetchone() is not None
            
            if user_exists and skip_exists:
                print(f"ℹ️  User '{email}' already exists. Skipping.")
                return False
            
            # Generate password hash
            password_hash = get_password_hash(password)
            
            if user_exists:
                # Update existing user
                conn.execute(
                    text("""
                        UPDATE users 
                        SET password_hash = :ph, 
                            is_superadmin = true,
                            updated_at = NOW()
                        WHERE email = :email
                    """),
                    {"ph": password_hash, "email": email}
                )
                conn.commit()
                print(f"✅ Updated admin user: {email}")
            else:
                # Create new user
                conn.execute(
                    text("""
                        INSERT INTO users 
                        (id, email, username, password_hash, first_name, last_name, 
                         is_active, is_superadmin, email_verified, created_at, updated_at)
                        VALUES 
                        (:id, :email, :username, :ph, :fn, :ln, true, true, true, NOW(), NOW())
                    """),
                    {
                        "id": f"admin-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                        "email": email,
                        "username": username,
                        "ph": password_hash,
                        "fn": first_name,
                        "ln": last_name,
                    }
                )
                conn.commit()
                print(f"✅ Created admin user: {email}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error seeding admin user: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Seed admin user for Cloud Platform"
    )
    parser.add_argument("email", nargs="?", help="Admin email address")
    parser.add_argument("--username", help="Admin username")
    parser.add_argument("--password", help="Admin password")
    parser.add_argument("--first-name", help="Admin first name")
    parser.add_argument("--last-name", help="Admin last name")
    parser.add_argument("--force", action="store_true", help="Update existing user")
    
    args = parser.parse_args()
    
    success = seed_admin_user(
        email=args.email,
        username=args.username,
        password=args.password,
        first_name=args.first_name,
        last_name=args.last_name,
        skip_exists=not args.force
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
