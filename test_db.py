print("Starting...")
try:
    from app.core.database import engine
    from sqlalchemy import text
    print("Imports successful")
    
    with engine.connect() as conn:
        print("Connection successful")
        result = conn.execute(text("SELECT 1"))
        print(f"Query result: {result.fetchone()}")
        print("Database connection working!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

