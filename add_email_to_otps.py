#!/usr/bin/env python3
"""
Migration script to add email column to otps table
"""

import sqlite3
import os
import sys
from pathlib import Path

def add_email_column():
    """Add email column to otps table"""

    # Get database path
    current_dir = Path(__file__).parent
    db_path = current_dir / "shawarma_local.db"

    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False

    try:
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check if email column already exists
        cursor.execute("PRAGMA table_info(otps)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if 'email' in column_names:
            print("Email column already exists in otps table")
            conn.close()
            return True

        # Add email column
        print("Adding email column to otps table...")
        cursor.execute("ALTER TABLE otps ADD COLUMN email VARCHAR(255)")

        # Create index on email column
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_otps_email ON otps(email)")

        conn.commit()
        conn.close()

        print("Migration completed successfully!")
        return True

    except Exception as e:
        print(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = add_email_column()
    sys.exit(0 if success else 1)
