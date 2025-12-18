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
        return self.MYSQLHOST or self.DB_HOST or "localhost"
    
    @property
    def database_port(self) -> int:
        """Get database port - Railway MYSQL_PORT takes priority"""
        return self.MYSQL_PORT or self.DB_PORT or 3306
    
    @property
    def database_user(self) -> str:
        """Get database user - Railway MYSQLUSER takes priority"""
        return self.MYSQLUSER or self.DB_USER or "root"
    
    @property
    def database_password(self) -> str:
        """Get database password - Railway MYSQL_ROOT_PASSWORD takes priority"""
        return self.MYSQL_ROOT_PASSWORD or self.DB_PASSWORD or ""
    
    @property
    def database_name(self) -> str:
        """Get database name - Railway MYSQL_DATABASE takes priority"""
        return self.MYSQL_DATABASE or self.DB_NAME or "shwarma"
    
    @property
    def DATABASE_URL(self) -> str:
        """Build MySQL connection URL"""
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

