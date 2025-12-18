"""Check staff table column types"""
from app.core.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SHOW COLUMNS FROM staff WHERE Field IN ('role', 'status')"))
        rows = result.fetchall()
        if rows:
            print("Current column types:")
            for row in rows:
                print(f"  {row[0]}: {row[1]}")
        else:
            print("No columns found")
except Exception as e:
    print(f"Error: {e}")

