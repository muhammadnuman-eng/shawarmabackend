#!/usr/bin/env python3
"""
Check what tables and data exist in the SQLite database
"""
from sqlalchemy import create_engine, text, MetaData, Table
import os

def check_sqlite_db():
    """Check SQLite database contents"""
    db_path = "./shawarma_local.db"
    if not os.path.exists(db_path):
        print(f"SQLite database not found at {db_path}")
        return

    engine = create_engine(f"sqlite:///{db_path}", echo=False)

    try:
        with engine.connect() as conn:
            # Get all tables
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = result.fetchall()

            print(f"Found {len(tables)} tables in SQLite database:")
            for table_name, in tables:
                # Count records in each table
                try:
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = count_result.fetchone()[0]
                    print(f"  - {table_name}: {count} records")
                except Exception as e:
                    print(f"  - {table_name}: Error counting records - {e}")

    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_sqlite_db()
