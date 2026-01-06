from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os

# Database connection - supports PostgreSQL, MySQL and SQLite with fallback
def create_database_engine():
    """Create database engine with support for PostgreSQL, MySQL, and SQLite"""
    database_url = settings.database_url
    print(f"DATABASE: Initial database_url from settings: {database_url}")

    # Force SQLite for local development if no database environment variables
    if (not os.getenv('MYSQLHOST') and
        not os.getenv('DB_HOST') and
        not os.getenv('PGHOST') and
        not os.getenv('POSTGRES_HOST') and
        not os.getenv('DATABASE_URL')):
        database_url = "sqlite:///./shawarma_local.db"
        print("INFO: Using SQLite for local development")
    print(f"DATABASE: Final database_url: {database_url}")

    # Try to create engine
    try:
        if database_url.startswith('sqlite'):
            # SQLite configuration
            engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},  # Required for SQLite
                echo=False
            )
        elif database_url.startswith('postgresql'):
            # PostgreSQL connection with proper settings
            engine = create_engine(
                database_url,
                pool_pre_ping=True,  # Verify connections before using
                pool_recycle=3600,   # Recycle connections after 1 hour
                echo=False,          # Set to True for SQL query logging
                # PostgreSQL-specific settings
                pool_size=10,        # Connection pool size
                max_overflow=20      # Max overflow connections
            )
        elif database_url.startswith('mysql'):
            # MySQL connection with proper settings (for backward compatibility)
            engine = create_engine(
                database_url,
                pool_pre_ping=True,  # Verify connections before using
                pool_recycle=3600,   # Recycle connections after 1 hour
                echo=False           # Set to True for SQL query logging
            )
        else:
            # Default configuration for other database types
            engine = create_engine(
                database_url,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
        return engine
    except Exception as e:
        print(f"WARNING: Failed to create database engine: {e}")
        print("INFO: Falling back to SQLite database")
        # Fallback to SQLite if connection fails
        return create_engine(
            "sqlite:///./shawarma_local.db",
            connect_args={"check_same_thread": False},
            echo=False
        )

engine = create_database_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

