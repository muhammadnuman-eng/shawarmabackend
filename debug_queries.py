import sys
sys.path.append('.')
from app.core.database import SessionLocal
from app.models.menu import MenuItem
from app.models.order import Order, OrderItem
from sqlalchemy import func, desc, or_, and_
from datetime import datetime, timedelta

def test_queries():
    db = SessionLocal()
    try:
        print("=== Testing Basic Queries ===")

        # Test 1: Basic product query
        products = db.query(MenuItem).filter(MenuItem.is_available == True).limit(3).all()
        print(f"Basic products query: {len(products)} found")

        # Test 2: Recent orders subquery
        print("\n=== Testing Recent Orders Subquery ===")
        seven_days_ago = datetime.now() - timedelta(days=7)

        recent_orders = db.query(
            OrderItem.menu_item_id,
            func.count(OrderItem.id).label('recent_order_count')
        ).join(Order, OrderItem.order_id == Order.id).filter(
            Order.created_at >= seven_days_ago,
            Order.status.not_in(['cancelled', 'Cancelled'])
        ).group_by(OrderItem.menu_item_id).all()

        print(f"Recent orders subquery: {len(recent_orders)} items found")

        # Test 3: High-demand query
        print("\n=== Testing High-Demand Query ===")

        recent_orders_subquery = db.query(
            OrderItem.menu_item_id,
            func.count(OrderItem.id).label('recent_order_count')
        ).join(Order, OrderItem.order_id == Order.id).filter(
            Order.created_at >= seven_days_ago,
            Order.status.not_in(['cancelled', 'Cancelled'])
        ).group_by(OrderItem.menu_item_id).subquery()

        products_query = db.query(
            MenuItem,
            func.coalesce(recent_orders_subquery.c.recent_order_count, 0).label('recent_orders'),
            (MenuItem.order_count * 0.3 + func.coalesce(recent_orders_subquery.c.recent_order_count, 0) * 0.7).label('demand_score')
        ).outerjoin(
            recent_orders_subquery,
            MenuItem.id == recent_orders_subquery.c.menu_item_id
        ).filter(
            MenuItem.is_available == True
        )

        products_with_scores = products_query.order_by(
            desc('demand_score'),
            MenuItem.rating.desc(),
            MenuItem.price.desc()
        ).limit(3).all()

        print(f"High-demand query: {len(products_with_scores)} products found")
        for product_data in products_with_scores:
            product = product_data[0]
            recent_orders = product_data[1] or 0
            demand_score = product_data[2] or 0
            print(f"  - {product.name}: Recent={recent_orders}, Score={demand_score:.2f}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_queries()
