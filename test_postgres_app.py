#!/usr/bin/env python3
"""
Test that the application can connect to PostgreSQL
"""
import os

# Set the DATABASE_URL
os.environ['DATABASE_URL'] = 'postgresql://postgres:test123@localhost:5432/shawarmabackend'

from app.core.database import engine
from sqlalchemy import text

def test_app_connection():
    """Test application connection to PostgreSQL"""
    try:
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text('SELECT version()'))
            version = result.fetchone()
            print(f"Connected to PostgreSQL: {version[0]}")

            # Test data migration
            result = conn.execute(text('SELECT COUNT(*) FROM users'))
            user_count = result.fetchone()[0]
            print(f"Users in database: {user_count}")

            result = conn.execute(text('SELECT COUNT(*) FROM otps'))
            otp_count = result.fetchone()[0]
            print(f"OTPs in database: {otp_count}")

            print("SUCCESS: Application can connect to PostgreSQL and access migrated data!")
            return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_app_connection()
