#!/usr/bin/env python3
"""
Migration script to add OAuth fields to users table
Run this after updating the User model
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text

# Database configuration - you may need to adjust these
DB_HOST = os.getenv("MYSQLHOST") or os.getenv("DB_HOST") or "localhost"
DB_PORT = os.getenv("MYSQLPORT") or os.getenv("DB_PORT") or "3306"
DB_USER = os.getenv("MYSQLUSER") or os.getenv("DB_USER") or "root"
DB_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD") or os.getenv("DB_PASSWORD") or ""
DB_NAME = os.getenv("MYSQL_DATABASE") or os.getenv("DB_NAME") or "shwarma"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

def add_oauth_fields():
    """Add provider and provider_id columns to users table"""

    print(f"Connecting to database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print(f"Using user: {DB_USER}")

    # Create engine
    engine = create_engine(DATABASE_URL)

    try:
        # Add columns using raw SQL
        with engine.connect() as conn:
            # Check if columns already exist
            result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'provider'"))
            if not result.fetchone():
                print("Adding provider column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN provider VARCHAR(50) NULL"))
                conn.commit()
                print("✅ Provider column added successfully!")
            else:
                print("Provider column already exists.")

            result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'provider_id'"))
            if not result.fetchone():
                print("Adding provider_id column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN provider_id VARCHAR(255) NULL"))
                conn.commit()
                print("✅ Provider_id column added successfully!")
            else:
                print("Provider_id column already exists.")

            print("Migration completed successfully!")

    except Exception as e:
        print(f"❌ Error during migration: {e}")
        print("Please check your database connection and credentials.")

if __name__ == "__main__":
    add_oauth_fields()
