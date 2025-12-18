"""
Database setup script - Creates initial data for development
Run this after setting up the database
"""
from app.core.database import SessionLocal, engine, Base
from app.models.menu import Category
from app.models.customer import Customer, MembershipType
from app.models.staff import Staff, StaffRole, StaffStatus
from app.models.role import Role, Permission
import uuid

# Create all tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Create default categories
    categories = [
        {"name": "Fatayers", "description": "Traditional fatayer items"},
        {"name": "Shawarma", "description": "Shawarma varieties"},
        {"name": "Appetizers", "description": "Appetizers and starters"},
        {"name": "Desserts", "description": "Sweet treats"},
        {"name": "Drinks", "description": "Beverages"},
    ]
    
    for cat_data in categories:
        existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if not existing:
            category = Category(
                id=str(uuid.uuid4()),
                **cat_data
            )
            db.add(category)
    
    # Create default permissions
    permissions_data = [
        {"name": "view-orders", "label": "View Orders", "category": "orders"},
        {"name": "update-order-status", "label": "Update Order Status", "category": "orders"},
        {"name": "add-edit-items", "label": "Add/Edit Items", "category": "menu"},
        {"name": "manage-categories", "label": "Manage Categories", "category": "menu"},
        {"name": "add-edit-staff", "label": "Add / Edit Staff", "category": "staff"},
        {"name": "assign-role", "label": "Assign Role", "category": "staff"},
        {"name": "view-earnings-reports", "label": "View Earnings & Reports", "category": "finance"},
        {"name": "view-branches", "label": "View Branches", "category": "finance"},
        {"name": "loyalty-rewards", "label": "Loyalty & Rewards", "category": "other"},
        {"name": "reviews-ratings", "label": "Reviews & Ratings", "category": "other"},
    ]
    
    for perm_data in permissions_data:
        existing = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        if not existing:
            permission = Permission(
                id=str(uuid.uuid4()),
                **perm_data
            )
            db.add(permission)
    
    db.commit()
    print("✅ Database setup completed successfully!")
    print("✅ Default categories and permissions created")
    
except Exception as e:
    db.rollback()
    print(f"❌ Error setting up database: {e}")
finally:
    db.close()

