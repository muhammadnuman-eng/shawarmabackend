print("Starting...")
try:
    from app.core.database import SessionLocal, engine
    from app.models.user import PromoCode
    from app.models.order import Order
    from sqlalchemy import text
    print("Imports successful")

    # Test database connection
    with engine.connect() as conn:
        print("Connection successful")
        result = conn.execute(text("SELECT 1"))
        print(f"Query result: {result.fetchone()}")
        print("Database connection working!")

    # Check promo codes
    db = SessionLocal()
    try:
        promos = db.query(PromoCode).all()
        print(f"\nFound {len(promos)} promo codes:")
        for p in promos:
            print(f"  {p.code}: active={p.is_active}, discount={p.discount_value}{'%' if p.discount_type == 'percentage' else 'Rs'}")

        # Check recent orders
        orders = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()
        print(f"\nFound {len(orders)} recent orders:")
        for o in orders:
            items_count = len(o.order_items) if o.order_items else 0
            print(f"  {o.order_number}: {o.status} - {o.total}Rs - {items_count} items")
    finally:
        db.close()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

