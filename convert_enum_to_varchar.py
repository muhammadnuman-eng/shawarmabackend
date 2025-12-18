"""
Convert staff enum columns to VARCHAR to avoid SQLAlchemy enum caching issues
"""
import sys
from app.core.database import engine
from sqlalchemy import text

def convert_enum_to_varchar():
    """Convert enum columns to VARCHAR"""
    with engine.connect() as conn:
        try:
            sys.stdout.write("Checking current column types...\n")
            sys.stdout.flush()
            result = conn.execute(text("SHOW COLUMNS FROM staff WHERE Field IN ('role', 'status')"))
            rows = list(result)
            for row in rows:
                sys.stdout.write(f"  {row[0]}: {row[1]}\n")
            sys.stdout.flush()
            
            sys.stdout.write("\nConverting role column from ENUM to VARCHAR...\n")
            sys.stdout.flush()
            conn.execute(text("""
                ALTER TABLE staff 
                MODIFY COLUMN role VARCHAR(50) NOT NULL
            """))
            
            sys.stdout.write("Converting status column from ENUM to VARCHAR...\n")
            sys.stdout.flush()
            conn.execute(text("""
                ALTER TABLE staff 
                MODIFY COLUMN status VARCHAR(50) DEFAULT 'On-Duty'
            """))
            
            conn.commit()
            sys.stdout.write("\n✅ Columns converted to VARCHAR successfully!\n")
            sys.stdout.write("Note: SQLAlchemy will now handle enum validation in Python code.\n")
            sys.stdout.flush()
            
            sys.stdout.write("\nVerifying conversion...\n")
            sys.stdout.flush()
            result = conn.execute(text("SHOW COLUMNS FROM staff WHERE Field IN ('role', 'status')"))
            rows = list(result)
            for row in rows:
                sys.stdout.write(f"  {row[0]}: {row[1]}\n")
            sys.stdout.flush()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            raise

if __name__ == "__main__":
    print("Converting enum columns to VARCHAR...")
    convert_enum_to_varchar()
    print("Done! Restart your server now.")

