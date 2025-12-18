from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # MySQL Database Configuration - Support both Railway and custom variables
    # Railway provides: MYSQLHOST, MYSQLPORT, MYSQLUSER, MYSQL_ROOT_PASSWORD, MYSQL_DATABASE
    # Custom variables: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
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
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
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
    def DATABASE_URL(self) -> str:
        """Build MySQL connection URL"""
        host = self.database_host
        port = self.database_port
        user = self.database_user
        password = self.database_password
        database = self.database_name
        
        # Debug logging (will show in Railway logs)
        import sys
        sys.stderr.write(f"[DB Config] Host: {host}, Port: {port}, User: {user}, Database: {database}\n")
        sys.stderr.write(f"[DB Config] MYSQLHOST env: {os.getenv('MYSQLHOST')}\n")
        sys.stderr.write(f"[DB Config] MYSQL_DATABASE env: {os.getenv('MYSQL_DATABASE')}\n")
        sys.stderr.flush()
        
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

