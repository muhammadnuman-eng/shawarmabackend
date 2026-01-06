from app.core.database import SessionLocal
from app.models.user import PromoCode
from datetime import datetime, timedelta
import uuid

db = SessionLocal()
try:
    # Check existing promo codes
    existing = db.query(PromoCode).all()
    print(f'Existing promo codes: {len(existing)}')
    for p in existing:
        print(f'  {p.code}: active={p.is_active}, expires={p.expires_at}')

    # Create promo codes if they don't exist
    promo_codes = [
        {
            'id': str(uuid.uuid4()),
            'code': 'WELCOME10',
            'discount_type': 'percentage',
            'discount_value': 10.0,
            'min_order_amount': 200.0,
            'max_discount': 50.0,
            'is_active': True,
            'expires_at': datetime.utcnow() + timedelta(days=30),
            'usage_limit': None,
            'used_count': 0
        },
        {
            'id': str(uuid.uuid4()),
            'code': 'SAVE20',
            'discount_type': 'fixed',
            'discount_value': 20.0,
            'min_order_amount': 150.0,
            'max_discount': None,
            'is_active': True,
            'expires_at': datetime.utcnow() + timedelta(days=15),
            'usage_limit': 100,
            'used_count': 0
        },
        {
            'id': str(uuid.uuid4()),
            'code': 'FIRSTORDER',
            'discount_type': 'percentage',
            'discount_value': 15.0,
            'min_order_amount': 100.0,
            'max_discount': 75.0,
            'is_active': True,
            'expires_at': datetime.utcnow() + timedelta(days=60),
            'usage_limit': None,
            'used_count': 0
        }
    ]

    for promo_data in promo_codes:
        existing_promo = db.query(PromoCode).filter(PromoCode.code == promo_data['code']).first()
        if not existing_promo:
            promo = PromoCode(**promo_data)
            db.add(promo)
            print(f'Created promo code: {promo_data["code"]}')
        else:
            print(f'Promo code already exists: {promo_data["code"]}')

    db.commit()
    print('Promo codes setup complete')

except Exception as e:
    print(f'Error: {e}')
    db.rollback()
finally:
    db.close()












