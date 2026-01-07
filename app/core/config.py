from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # MySQL Database Configuration - Support both Railway and custom variables
    # Railway provides: MYSQLHOST, MYSQLPORT, MYSQLUSER, MYSQL_ROOT_PASSWORD, MYSQL_DATABASE
    # Custom variables: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
    # Direct DATABASE_URL for Railway or other complete connection strings
    DATABASE_URL: Optional[str] = None

    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_NAME: Optional[str] = None
    
    # Railway MySQL variables
    MYSQLHOST: Optional[str] = None
    MYSQL_PORT: Optional[int] = None
    MYSQLUSER: Optional[str] = None
    MYSQL_ROOT_PASSWORD: Optional[str] = None
    MYSQL_DATABASE: Optional[str] = None
    
    # Application Settings
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://10.147.118.151:8081,http://10.147.118.151:3000,http://10.147.118.151,http://192.168.100.125:8081,http://192.168.100.125:3000,http://192.168.100.125"

    # SMS Service Configuration (Twilio)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None

    # SMS Settings
    SMS_ENABLED: bool = True  # Set to True in production
    SMS_PROVIDER: str = "twilio"  # 'twilio', 'aws_sns', etc.

    # Email Service Configuration
    EMAIL_ENABLED: bool = False  # Set to True in production
    EMAIL_PROVIDER: str = "smtp"  # 'smtp', 'sendgrid', etc.

    # SMTP Configuration (support both naming conventions)
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: Optional[str] = None

    # Alternative email config variables (user provided)
    EMAIL_SERVICE: Optional[str] = None  # 'gmail', etc.
    EMAIL_HOST: Optional[str] = None
    EMAIL_PORT: Optional[int] = None
    EMAIL_SECURE: Optional[str] = None  # 'true'/'false'
    EMAIL_USER: Optional[str] = None
    EMAIL_PASS: Optional[str] = None

    # SendGrid Configuration (for EMAIL_PROVIDER="sendgrid")
    SENDGRID_API_KEY: Optional[str] = None

    # OAuth Configuration
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    # Google Maps API Configuration
    GOOGLE_MAPS_API_KEY: Optional[str] = "AIzaSyB8dti-R6Ky04fwToZ4mam0FQ2ksF1Xek0"  # Updated Google Maps API key

    # Google AI API Configuration
    GEMINI_API_KEY: Optional[str] = None
    STT_API_KEY: Optional[str] = None

    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None

    # OAuth Settings
    OAUTH_ENABLED: bool = False  # Set to True in production

    # Location Service Settings
    LOCATION_CACHE_ENABLED: bool = True  # Enable caching for location requests
    LOCATION_CACHE_TTL: int = 3600  # Cache TTL in seconds (1 hour)
    LOCATION_RATE_LIMIT: int = 100  # Requests per minute per IP
    
    @property
    def database_host(self) -> str:
        """Get database host - Railway MYSQLHOST takes priority"""
        # Try Railway variables first (using os.getenv for reliability)
        host = os.getenv("MYSQLHOST") or self.MYSQLHOST or os.getenv("DB_HOST") or self.DB_HOST
        return host or "localhost"
    
    @property
    def database_port(self) -> int:
        """Get database port - Railway MYSQL_PORT takes priority"""
        # Try Railway variables first (using os.getenv for reliability)
        port_str = os.getenv("MYSQLPORT") or os.getenv("MYSQL_PORT")
        if port_str:
            try:
                return int(port_str)
            except ValueError:
                pass
        if self.MYSQL_PORT:
            return self.MYSQL_PORT
        port_str = os.getenv("DB_PORT")
        if port_str:
            try:
                return int(port_str)
            except ValueError:
                pass
        return self.DB_PORT or 3306
    
    @property
    def database_user(self) -> str:
        """Get database user - Railway MYSQLUSER takes priority"""
        # Try Railway variables first (using os.getenv for reliability)
        user = os.getenv("MYSQLUSER") or self.MYSQLUSER or os.getenv("DB_USER") or self.DB_USER
        return user or "root"
    
    @property
    def database_password(self) -> str:
        """Get database password - Railway MYSQL_ROOT_PASSWORD takes priority"""
        # Try Railway variables first (using os.getenv for reliability)
        password = os.getenv("MYSQL_ROOT_PASSWORD") or self.MYSQL_ROOT_PASSWORD or os.getenv("DB_PASSWORD") or self.DB_PASSWORD
        return password or ""
    
    @property
    def database_name(self) -> str:
        """Get database name - Railway MYSQL_DATABASE takes priority"""
        # Try Railway variables first (using os.getenv for reliability)
        database = os.getenv("MYSQL_DATABASE") or self.MYSQL_DATABASE or os.getenv("DB_NAME") or self.DB_NAME
        return database or "shwarma"
    
    @property
    def database_url(self) -> str:
        """Build database connection URL - supports PostgreSQL, MySQL, or SQLite"""
        # If DATABASE_URL is provided directly, use it (supports PostgreSQL URLs)
        if self.DATABASE_URL:
            return self.DATABASE_URL

        # For local development without explicit DATABASE_URL, use SQLite
        # This prevents the need for database setup during development
        import os
        if os.getenv('ENVIRONMENT') != 'production' and not any([
            os.getenv('MYSQLHOST'), os.getenv('DB_HOST'),
            os.getenv('PGHOST'), os.getenv('POSTGRES_HOST'),
            self.MYSQLHOST, self.DB_HOST
        ]):
            return "sqlite:///./shawarma_local.db"

        # Check if PostgreSQL environment variables are set
        pg_host = os.getenv('PGHOST') or os.getenv('POSTGRES_HOST')
        if pg_host:
            # Build PostgreSQL connection
            pg_port = os.getenv('PGPORT') or os.getenv('POSTGRES_PORT') or '5432'
            pg_user = os.getenv('PGUSER') or os.getenv('POSTGRES_USER') or 'postgres'
            pg_password = os.getenv('PGPASSWORD') or os.getenv('POSTGRES_PASSWORD') or ''
            pg_database = os.getenv('PGDATABASE') or os.getenv('POSTGRES_DB') or 'shawarmabackend'

            password_part = f":{pg_password}" if pg_password else ""
            return f"postgresql+psycopg2://{pg_user}{password_part}@{pg_host}:{pg_port}/{pg_database}"

        # Otherwise, build MySQL connection from components (for backward compatibility)
        host = self.database_host
        port = self.database_port
        user = self.database_user
        password = self.database_password
        database = self.database_name

        password_part = f":{password}" if password else ""
        return f"mysql+pymysql://{user}{password_part}@{host}:{port}/{database}?charset=utf8mb4"
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS string to list"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return ["http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

