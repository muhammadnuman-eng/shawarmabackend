from app.core.database import SessionLocal
from app.models.menu import MenuItem
from app.models.user import PromoCode
import random
from datetime import datetime, timedelta
import uuid

def add_sample_data():
    db = SessionLocal()

    try:
        # Get all products
        products = db.query(MenuItem).all()

        print(f'Adding sample data to {len(products)} products...')

        # Add sample ratings and order counts
        for i, product in enumerate(products):
            # Add realistic ratings (3.5-5.0)
            product.rating = round(random.uniform(3.5, 5.0), 1)

            # Add realistic order counts (some popular, some not)
            if i < 3:  # First 3 products are "popular"
                product.order_count = random.randint(50, 200)
            elif i < 8:  # Next 5 are moderately popular
                product.order_count = random.randint(10, 50)
            else:  # Rest have fewer orders
                product.order_count = random.randint(0, 10)

            # Make sure reviews_count matches rating logic
            product.reviews_count = max(1, product.order_count // 3)  # Roughly 1 review per 3 orders

        # Add sample promo codes
        promo_codes = [
            {
                "id": str(uuid.uuid4()),
                "code": "WELCOME10",
                "discount_type": "percentage",
                "discount_value": 10.0,
                "min_order_amount": 200.0,
                "max_discount": 50.0,
                "is_active": True,
                "expires_at": datetime.utcnow() + timedelta(days=30),
                "usage_limit": None,
                "used_count": 0
            },
            {
                "id": str(uuid.uuid4()),
                "code": "SAVE20",
                "discount_type": "fixed",
                "discount_value": 20.0,
                "min_order_amount": 150.0,
                "max_discount": None,
                "is_active": True,
                "expires_at": datetime.utcnow() + timedelta(days=15),
                "usage_limit": 100,
                "used_count": 0
            },
            {
                "id": str(uuid.uuid4()),
                "code": "FIRSTORDER",
                "discount_type": "percentage",
                "discount_value": 15.0,
                "min_order_amount": 100.0,
                "max_discount": 75.0,
                "is_active": True,
                "expires_at": datetime.utcnow() + timedelta(days=60),
                "usage_limit": None,
                "used_count": 0
            }
        ]

        for promo_data in promo_codes:
            # Check if promo code already exists
            existing_promo = db.query(PromoCode).filter(PromoCode.code == promo_data["code"]).first()
            if not existing_promo:
                promo = PromoCode(**promo_data)
                db.add(promo)
                print(f"Added promo code: {promo_data['code']}")

        db.commit()
        print('Sample data added successfully!')

        # Show updated data
        print('\nUpdated products:')
        for product in products[:5]:
            print(f'  {product.name}: Rating={product.rating}, Orders={product.order_count}')

        print('\nPromo codes:')
        promos = db.query(PromoCode).all()
        for promo in promos:
            print(f'  {promo.code}: {promo.discount_value}{"%" if promo.discount_type == "percentage" else "Rs"} off (Min: {promo.min_order_amount}Rs)')

    except Exception as e:
        print(f'Error: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_data()
