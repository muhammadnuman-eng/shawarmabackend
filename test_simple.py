#!/usr/bin/env python3

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Test imports
    from app.main import app
    print("✅ Backend app imported successfully")

    from app.api.v1.products import router
    print("✅ Products router imported successfully")

    from app.models.menu import MenuItem, Category
    print("✅ Models imported successfully")

    from app.models.order import Order, OrderItem
    print("✅ Order models imported successfully")

    # Test database connection
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        # Test if we can query categories
        categories = db.query(Category).limit(5).all()
        print(f"✅ Database connection works - found {len(categories)} categories")

        # Test if we can query products
        products = db.query(MenuItem).limit(5).all()
        print(f"✅ Products query works - found {len(products)} products")

    except Exception as e:
        print(f"❌ Database query error: {e}")
    finally:
        db.close()

    print("\n🎉 All basic tests passed!")

except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
