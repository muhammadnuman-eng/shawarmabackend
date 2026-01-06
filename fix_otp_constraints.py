#!/usr/bin/env python3
"""
Fix OTP table constraints to make phone_number nullable
"""

import sqlite3
import os
import sys
from pathlib import Path

def fix_otp_constraints():
    """Make phone_number nullable in otps table"""

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

        # Check current constraints
        cursor.execute("PRAGMA table_info(otps)")
        columns = cursor.fetchall()
        phone_nullable = next((col[3] == 0 for col in columns if col[1] == 'phone_number'), None)

        if phone_nullable:
            print("phone_number is already nullable")
            conn.close()
            return True

        print("Making phone_number nullable...")

        # SQLite doesn't support ALTER COLUMN directly for constraints
        # We need to recreate the table
        # First, backup existing data
        cursor.execute("SELECT * FROM otps")
        existing_data = cursor.fetchall()

        # Get column names
        cursor.execute("PRAGMA table_info(otps)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        # Drop and recreate table with correct constraints
        cursor.execute("""
        CREATE TABLE otps_new (
            id VARCHAR(36) PRIMARY KEY NOT NULL,
            phone_number VARCHAR(20),
            email VARCHAR(255),
            otp_code VARCHAR(6) NOT NULL,
            purpose VARCHAR(50) NOT NULL,
            is_verified BOOLEAN DEFAULT 0,
            expires_at DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Copy data
        placeholders = ','.join('?' * len(column_names))
        cursor.executemany(f"INSERT INTO otps_new ({','.join(column_names)}) VALUES ({placeholders})", existing_data)

        # Drop old table and rename new one
        cursor.execute("DROP TABLE otps")
        cursor.execute("ALTER TABLE otps_new RENAME TO otps")

        # Recreate index
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_otps_email ON otps(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_otps_phone_number ON otps(phone_number)")

        conn.commit()
        conn.close()

        print("Migration completed successfully!")
        return True

    except Exception as e:
        print(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_otp_constraints()
    sys.exit(0 if success else 1)
