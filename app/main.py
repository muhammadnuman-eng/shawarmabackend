from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import (
    orders, customers, staff, menu, transactions, reviews, roles, dashboard,
    auth, user, products, search, cart, addresses, mobile_orders, payment,
    favorites, mobile_reviews, notifications, loyalty, location, chat, admin
)
import sys

# Create database tables (with error handling)
try:
    import sys
    sys.stderr.write(f"[Startup] Database URL: {settings.DATABASE_URL.replace(settings.database_password, '***') if settings.database_password else settings.DATABASE_URL}\n")
    sys.stderr.flush()
    Base.metadata.create_all(bind=engine)
    sys.stderr.write("[Startup] Database tables created successfully\n")
    sys.stderr.flush()
except Exception as e:
    sys.stderr.write(f"[Startup] Warning: Could not create database tables: {e}\n")
    sys.stderr.write(f"[Startup] Database connection will be attempted on first request\n")
    sys.stderr.flush()

app = FastAPI(
    title="Shawarma Stop API",
    description="Backend API for Shawarma Stop - Admin Panel & Mobile App",
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Admin Panel Routers (existing)
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(customers.router, prefix="/api/v1/customers", tags=["Customers"])
app.include_router(staff.router, prefix="/api/v1/staff", tags=["Staff"])
app.include_router(menu.router, prefix="/api/v1/menu", tags=["Menu"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["Reviews"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["Roles"])

# Mobile App Routers (new)
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/api/user", tags=["User/Profile"])
app.include_router(products.router, prefix="/api", tags=["Products"])
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(cart.router, prefix="/api", tags=["Cart"])
app.include_router(addresses.router, prefix="/api", tags=["Addresses"])
app.include_router(mobile_orders.router, prefix="/api", tags=["Mobile Orders"])
app.include_router(payment.router, prefix="/api", tags=["Payment"])
app.include_router(favorites.router, prefix="/api", tags=["Favorites"])
app.include_router(mobile_reviews.router, prefix="/api", tags=["Mobile Reviews"])
app.include_router(notifications.router, prefix="/api", tags=["Notifications"])
app.include_router(loyalty.router, prefix="/api", tags=["Loyalty"])
app.include_router(location.router, prefix="/api", tags=["Location"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(admin.router, prefix="/api", tags=["Admin"])

@app.get("/")
async def root():
    return {"message": "Shawarma Stop Admin API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/test")
async def test_routes():
    """Test endpoint to verify API routes are working"""
    return {
        "message": "API routes are working!",
        "routes": [
            "/api/v1/dashboard/stats",
            "/api/v1/orders/",
            "/api/v1/customers/",
            "/api/v1/staff/",
        ]
    }

