import uvicorn
import os
import sys

if __name__ == "__main__":
    # Ensure we're in the correct directory for .env file loading
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Add current directory to Python path so we can import app
    sys.path.insert(0, script_dir)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

