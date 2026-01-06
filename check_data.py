#!/usr/bin/env python3
import sys
import os
sys.path.append('.')

from app.core.database import SessionLocal
from app.models.user import PromoCode
from app.models.order import Order

def check_data():
    db = SessionLocal()
    try:
        # Check promo codes
        promos = db.query(PromoCode).all()
        print(f"Found {len(promos)} promo codes:")
        for p in promos:
            print(f"  {p.code}: active={p.is_active}, discount={p.discount_value}{'%' if p.discount_type == 'percentage' else 'Rs'}")

        # Check recent orders
        orders = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()
        print(f"\nFound {len(orders)} recent orders:")
        for o in orders:
            print(f"  {o.order_number}: {o.status} - {o.total}Rs - {len(o.order_items) if o.order_items else 0} items")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_data()












