from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

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

# Import and include routers
from app.api.v1 import (
    addresses, admin, auth, cart, categories, chat, customers, dashboard,
    favorites, location, loyalty, menu, mobile_orders, mobile_reviews,
    notifications, orders, payment, products, reviews, roles,
    search, sms_webhook, staff, transactions, user
)

# Include all API routers
app.include_router(addresses.router, prefix="/api/addresses", tags=["Addresses"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["Favorites"])
app.include_router(location.router, prefix="/api/location", tags=["Location"])
app.include_router(loyalty.router, prefix="/api/loyalty", tags=["Loyalty"])
app.include_router(menu.router, prefix="/api/menu", tags=["Menu"])
app.include_router(mobile_orders.router, prefix="/api/mobile/orders", tags=["Mobile Orders"])
app.include_router(mobile_reviews.router, prefix="/api/mobile/reviews", tags=["Mobile Reviews"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(payment.router, prefix="/api/payment", tags=["Payment"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(roles.router, prefix="/api/roles", tags=["Roles"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(sms_webhook.router, prefix="/api/sms-webhook", tags=["SMS Webhook"])
app.include_router(staff.router, prefix="/api/staff", tags=["Staff"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(user.router, prefix="/api/user", tags=["User"])

@app.get("/")
async def root():
    print("DEBUG: Root endpoint called!")
    return {"message": "Shawarma Stop API", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

