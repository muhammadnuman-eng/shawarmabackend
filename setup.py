from setuptools import setup, find_packages

setup(
    name="shawarma-store-backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "sqlalchemy==2.0.23",
        "pymysql==1.1.0",
        "cryptography==41.0.7",
        "pydantic==2.7.4",
        "pydantic-core==2.18.4",
        "pydantic-settings==2.3.4",
        "python-dotenv==1.0.0",
        "python-multipart==0.0.6",
        "passlib[bcrypt]==1.7.4",
        "python-jose[cryptography]==3.3.0",
        "alembic==1.12.1",
        "email-validator==2.1.0",
    ],
)
