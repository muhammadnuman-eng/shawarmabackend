from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.order import Order, OrderStatus
from app.models.transaction import Transaction, TransactionStatus
from app.schemas.dashboard import DashboardStats

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    # Total orders
    total_orders = db.query(Order).count()
    
    # Total delivery (Delivered + Delivering)
    total_delivery = db.query(Order).filter(
        Order.status.in_([OrderStatus.DELIVERED, OrderStatus.DELIVERING])
    ).count()
    
    # Cancelled orders
    cancelled_orders = db.query(Order).filter(
        Order.status == OrderStatus.CANCELLED
    ).count()
    
    # Total revenue (sum of all non-cancelled orders)
    total_revenue_result = db.query(func.sum(Order.total)).filter(
        Order.status != OrderStatus.CANCELLED
    ).scalar()
    total_revenue = float(total_revenue_result) if total_revenue_result else 0.0
    
    # Today's revenue
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_revenue_result = db.query(func.sum(Order.total)).filter(
        Order.status != OrderStatus.CANCELLED,
        Order.created_at >= today_start
    ).scalar()
    today_revenue = float(today_revenue_result) if today_revenue_result else 0.0
    
    # Refunds (cancelled orders total)
    refunds_result = db.query(func.sum(Order.total)).filter(
        Order.status == OrderStatus.CANCELLED
    ).scalar()
    refunds = float(refunds_result) if refunds_result else 0.0
    
    # Calculate percentage changes (comparing with previous period)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    prev_total_orders = db.query(Order).filter(Order.created_at < thirty_days_ago).count()
    orders_change = calculate_percentage_change(total_orders, prev_total_orders)
    
    prev_total_delivery = db.query(Order).filter(
        Order.status.in_([OrderStatus.DELIVERED, OrderStatus.DELIVERING]),
        Order.created_at < thirty_days_ago
    ).count()
    delivery_change = calculate_percentage_change(total_delivery, prev_total_delivery)
    
    prev_cancelled = db.query(Order).filter(
        Order.status == OrderStatus.CANCELLED,
        Order.created_at < thirty_days_ago
    ).count()
    cancelled_change = calculate_percentage_change(cancelled_orders, prev_cancelled)
    
    prev_revenue_result = db.query(func.sum(Order.total)).filter(
        Order.status != OrderStatus.CANCELLED,
        Order.created_at < thirty_days_ago
    ).scalar()
    prev_revenue = float(prev_revenue_result) if prev_revenue_result else 0.0
    revenue_change = calculate_percentage_change(total_revenue, prev_revenue)
    
    return DashboardStats(
        total_orders=total_orders,
        total_delivery=total_delivery,
        cancelled_orders=cancelled_orders,
        total_revenue=total_revenue,
        today_revenue=today_revenue,
        refunds=refunds,
        orders_change_percent=orders_change,
        delivery_change_percent=delivery_change,
        cancelled_change_percent=cancelled_change,
        revenue_change_percent=revenue_change
    )

def calculate_percentage_change(current: float, previous: float) -> str:
    """Calculate percentage change"""
    if previous == 0:
        return "+0% (30days)" if current > 0 else "0% (30days)"
    
    change = ((current - previous) / previous) * 100
    sign = "+" if change > 0 else ""
    return f"{sign}{change:.1f}% (30days)"

