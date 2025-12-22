#!/usr/bin/env python3
"""
Migration script to add OAuth fields to users table
Run this after updating the User model
"""

from sqlalchemy import create_engine, Column, String
from app.core.database import Base
from app.core.config import settings

def add_oauth_fields():
    """Add provider and provider_id columns to users table"""

    # Create engine
    engine = create_engine(settings.DATABASE_URL)

    # Add columns using raw SQL (since SQLAlchemy doesn't support adding columns easily)
    with engine.connect() as conn:
        # Check if columns already exist
        result = conn.execute("SHOW COLUMNS FROM users LIKE 'provider'")
        if not result.fetchone():
            print("Adding provider column...")
            conn.execute("ALTER TABLE users ADD COLUMN provider VARCHAR(50) NULL")
            conn.commit()

        result = conn.execute("SHOW COLUMNS FROM users LIKE 'provider_id'")
        if not result.fetchone():
            print("Adding provider_id column...")
            conn.execute("ALTER TABLE users ADD COLUMN provider_id VARCHAR(255) NULL")
            conn.commit()

        print("Migration completed successfully!")

if __name__ == "__main__":
    add_oauth_fields()
