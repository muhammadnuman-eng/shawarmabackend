"""
Fix staff table enum - Update enum column to match Python enum values
Run this script to update the database enum column
"""
from app.core.database import engine
from sqlalchemy import text

def fix_staff_enum():
    """Update staff table enum columns to match Python enum values"""
    with engine.connect() as conn:
        try:
            print("Checking current enum values...")
            
            # Check role enum
            result = conn.execute(text("""
                SHOW COLUMNS FROM staff WHERE Field = 'role'
            """))
            role_info = result.fetchone()
            if role_info:
                print(f"Current role enum: {role_info[1]}")
            
            # Check status enum
            result = conn.execute(text("""
                SHOW COLUMNS FROM staff WHERE Field = 'status'
            """))
            status_info = result.fetchone()
            if status_info:
                print(f"Current status enum: {status_info[1]}")
            
            print("\nUpdating role enum column...")
            # Drop and recreate role column with correct enum values
            conn.execute(text("""
                ALTER TABLE staff 
                MODIFY COLUMN role ENUM('Manager', 'Chef', 'Rider', 'Cashier') NOT NULL
            """))
            
            print("Updating status enum column...")
            # Drop and recreate status column with correct enum values
            conn.execute(text("""
                ALTER TABLE staff 
                MODIFY COLUMN status ENUM('On-Duty', 'Off Duty') DEFAULT 'On-Duty'
            """))
            
            conn.commit()
            print("✅ Enum columns updated successfully!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    print("Fixing staff table enum columns...")
    fix_staff_enum()
    print("Done!")

