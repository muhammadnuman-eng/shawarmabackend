from app.core.database import SessionLocal
from app.models.menu import Category, MenuItem
import uuid

def add_categories_and_products():
    db = SessionLocal()

    try:
        # First, add categories
        categories = [
            {"id": "cat_001", "name": "Chicken Shawarma", "description": "Authentic chicken shawarma dishes"},
            {"id": "cat_002", "name": "Beef Shawarma", "description": "Premium beef shawarma selections"},
            {"id": "cat_003", "name": "Lamb Shawarma", "description": "Traditional lamb shawarma dishes"},
            {"id": "cat_004", "name": "Vegetarian", "description": "Delicious vegetarian options"},
            {"id": "cat_005", "name": "Sides", "description": "Fries, rice bowls and sides"},
            {"id": "cat_006", "name": "Family Deals", "description": "Large portions and family meals"},
        ]

        for cat_data in categories:
            # Check if category already exists
            existing_cat = db.query(Category).filter(Category.id == cat_data["id"]).first()
            if not existing_cat:
                category = Category(
                    id=cat_data["id"],
                    name=cat_data["name"],
                    description=cat_data["description"]
                )
                db.add(category)
                print(f"Added category: {cat_data['name']}")

        db.commit()

        # Now add products
        products = [
            # Chicken Shawarma
            {
                "id": "prod_001",
                "name": "Classic Chicken Shawarma",
                "price": 250.00,
                "image": "https://images.unsplash.com/photo-1544025162-d76694265947?w=400",
                "description": "Tender chicken marinated in traditional spices, wrapped in warm pita bread with garlic sauce",
                "category_id": "cat_001",
                "rating": 4.5,
                "reviews_count": 25,
                "order_count": 120
            },
            {
                "id": "prod_002",
                "name": "Chicken Shawarma Plate",
                "price": 280.00,
                "image": "https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=400",
                "description": "Chicken shawarma with rice, salad, and traditional sauces",
                "category_id": "cat_001",
                "rating": 4.3,
                "reviews_count": 18,
                "order_count": 85
            },

            # Beef Shawarma
            {
                "id": "prod_003",
                "name": "Beef Shawarma Wrap",
                "price": 300.00,
                "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400",
                "description": "Slow-cooked beef with special blend of Middle Eastern spices, served with tahini",
                "category_id": "cat_002",
                "rating": 4.7,
                "reviews_count": 32,
                "order_count": 150
            },

            # Lamb Shawarma
            {
                "id": "prod_004",
                "name": "Lamb Shawarma Plate",
                "price": 350.00,
                "image": "https://images.unsplash.com/photo-1541599468348-e96984315621?w=400",
                "description": "Juicy lamb shawarma served on a bed of rice with salad and yogurt sauce",
                "category_id": "cat_003",
                "rating": 4.6,
                "reviews_count": 20,
                "order_count": 90
            },

            # Vegetarian
            {
                "id": "prod_005",
                "name": "Vegetarian Shawarma",
                "price": 200.00,
                "image": "https://images.unsplash.com/photo-1551782450-17144efb5723?w=400",
                "description": "Grilled vegetables and halloumi cheese with herbs, perfect for vegetarians",
                "category_id": "cat_004",
                "rating": 4.2,
                "reviews_count": 15,
                "order_count": 60
            },
            {
                "id": "prod_006",
                "name": "Falafel Shawarma",
                "price": 180.00,
                "image": "https://images.unsplash.com/photo-1593001874117-c99c800e3eb7?w=400",
                "description": "Crispy falafel balls with tahini sauce and fresh vegetables in pita bread",
                "category_id": "cat_004",
                "rating": 4.1,
                "reviews_count": 12,
                "order_count": 45
            },

            # Sides
            {
                "id": "prod_007",
                "name": "Shawarma Fries",
                "price": 150.00,
                "image": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400",
                "description": "Crispy fries topped with shawarma meat and special garlic sauce",
                "category_id": "cat_005",
                "rating": 4.4,
                "reviews_count": 22,
                "order_count": 100
            },
            {
                "id": "prod_008",
                "name": "Shawarma Rice Bowl",
                "price": 220.00,
                "image": "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=400",
                "description": "Shawarma meat over seasoned rice with vegetables and sauce",
                "category_id": "cat_005",
                "rating": 4.3,
                "reviews_count": 16,
                "order_count": 70
            },

            # Family Deals
            {
                "id": "prod_009",
                "name": "Mixed Grill Shawarma",
                "price": 400.00,
                "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400",
                "description": "Combination of chicken, beef, and lamb with all traditional accompaniments",
                "category_id": "cat_006",
                "rating": 4.8,
                "reviews_count": 28,
                "order_count": 65
            },
            {
                "id": "prod_010",
                "name": "Family Shawarma Deal",
                "price": 750.00,
                "image": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=400",
                "description": "Large family portion with multiple shawarmas, sides, and drinks",
                "category_id": "cat_006",
                "rating": 4.6,
                "reviews_count": 19,
                "order_count": 40
            },
            {
                "id": "prod_011",
                "name": "Mega Family Feast",
                "price": 2500.00,
                "image": "https://images.unsplash.com/photo-1544025162-d76694265947?w=400",
                "description": "Complete family meal with 5 shawarmas, large fries, drinks, and desserts",
                "category_id": "cat_006",
                "rating": 4.9,
                "reviews_count": 35,
                "order_count": 25
            },
            {
                "id": "prod_012",
                "name": "Ultimate Family Combo",
                "price": 3200.00,
                "image": "https://images.unsplash.com/photo-1555399624946-b28f40a0ca4b?w=400",
                "description": "Everything included: multiple meats, sides, drinks, and dessert platter",
                "category_id": "cat_006",
                "rating": 5.0,
                "reviews_count": 42,
                "order_count": 15
            },
            {
                "id": "prod_013",
                "name": "Party Size Deal",
                "price": 2800.00,
                "image": "https://images.unsplash.com/photo-1541599468348-e96984315621?w=400",
                "description": "Perfect for parties - serves 8-10 people with variety of items",
                "category_id": "cat_006",
                "rating": 4.7,
                "reviews_count": 24,
                "order_count": 30
            },
        ]

        for prod_data in products:
            # Check if product already exists
            existing_prod = db.query(MenuItem).filter(MenuItem.id == prod_data["id"]).first()
            if not existing_prod:
                product = MenuItem(
                    id=prod_data["id"],
                    name=prod_data["name"],
                    price=prod_data["price"],
                    image=prod_data["image"],
                    description=prod_data["description"],
                    category_id=prod_data["category_id"],
                    rating=prod_data["rating"],
                    reviews_count=prod_data["reviews_count"],
                    order_count=prod_data["order_count"],
                    is_available=True,
                    status="Available"
                )
                db.add(product)
                print(f"Added product: {prod_data['name']}")

        db.commit()
        print("\n✅ Successfully added categories and products to database!")

        # Show summary
        total_categories = db.query(Category).count()
        total_products = db.query(MenuItem).count()

        print(f"\n📊 Database Summary:")
        print(f"   Categories: {total_categories}")
        print(f"   Products: {total_products}")

        # Show products by category
        print(f"\n📋 Products by Category:")
        categories_db = db.query(Category).all()
        for cat in categories_db:
            products_in_cat = db.query(MenuItem).filter(MenuItem.category_id == cat.id).count()
            print(f"   {cat.name}: {products_in_cat} products")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    add_categories_and_products()
