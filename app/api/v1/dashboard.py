from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime, timedelta
from typing import List, Optional
from app.core.database import get_db
from app.models.order import Order, OrderStatus, OrderItem
from app.models.customer import Customer, MembershipType
from app.models.transaction import Transaction, TransactionStatus
from app.models.staff import Staff
from app.schemas.dashboard import (
    DashboardStats,
    ActiveOrderResponse,
    EarningBreakdownResponse,
    StaffListResponse,
    TopCustomerResponse
)
from app.schemas.order import OrderItemResponse

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

@router.get("/active-orders", response_model=List[ActiveOrderResponse])
def get_active_orders(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get active orders for dashboard"""
    query = db.query(Order).join(Customer, Order.customer_id == Customer.id)

    # Filter by active statuses only
    active_statuses = [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PREPARING,
                      OrderStatus.READY, OrderStatus.OUT_FOR_DELIVERY, OrderStatus.DELIVERED,
                      OrderStatus.PREPARING_OLD, OrderStatus.PICKUP, OrderStatus.DELIVERING, OrderStatus.DELIVERED_OLD]

    if status and status.lower() != 'all':
        if status.lower() == 'preparing':
            query = query.filter(or_(
                Order.status == OrderStatus.PREPARING,
                Order.status == OrderStatus.PREPARING_OLD
            ))
        elif status.lower() == 'delivering':
            query = query.filter(or_(
                Order.status == OrderStatus.OUT_FOR_DELIVERY,
                Order.status == OrderStatus.DELIVERING
            ))
        elif status.lower() == 'delivered':
            query = query.filter(or_(
                Order.status == OrderStatus.DELIVERED,
                Order.status == OrderStatus.DELIVERED_OLD
            ))
        else:
            query = query.filter(Order.status == status)
    else:
        query = query.filter(Order.status.in_(active_statuses))

    # Search filter
    if search:
        search_lower = search.lower()
        query = query.filter(
            or_(
                Order.order_number.ilike(f"%{search}%"),
                Customer.name.ilike(f"%{search}%"),
                Order.note.ilike(f"%{search}%")
            )
        )

    orders = query.order_by(Order.created_at.desc()).limit(limit).all()

    response = []
    for order in orders:
        # Get items string
        items_list = []
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for item in order_items:
            items_list.append(f"{item.item_name} x{item.quantity}")
        items_str = ", ".join(items_list) if items_list else "No items"

        # Map status for frontend compatibility
        status_mapped = order.status
        if order.status == OrderStatus.PREPARING_OLD:
            status_mapped = "Preparing"
        elif order.status == OrderStatus.OUT_FOR_DELIVERY:
            status_mapped = "Delivering"
        elif order.status == OrderStatus.DELIVERED_OLD:
            status_mapped = "Delivered"
        elif order.status == OrderStatus.DELIVERING:
            status_mapped = "Delivering"
        elif order.status == OrderStatus.PICKUP:
            status_mapped = "Pickup"

        response.append(ActiveOrderResponse(
            id=order.id,
            order_number=order.order_number,
            customer_name=order.customer.name if order.customer else "Unknown",
            status=status_mapped,
            items=items_str,
            amount=order.total,
            image_url=order.image_url,
            created_at=order.created_at
        ))

    return response

@router.get("/earning-breakdown", response_model=EarningBreakdownResponse)
def get_earning_breakdown(db: Session = Depends(get_db)):
    """Get earning breakdown statistics"""
    # Food sales (subtotal from non-cancelled orders)
    food_sales_result = db.query(func.sum(Order.subtotal)).filter(
        Order.status != OrderStatus.CANCELLED
    ).scalar()
    food_sales = float(food_sales_result) if food_sales_result else 0.0

    # Delivery fees (from non-cancelled orders)
    delivery_fees_result = db.query(func.sum(Order.delivery_fee)).filter(
        Order.status != OrderStatus.CANCELLED
    ).scalar()
    delivery_fees = float(delivery_fees_result) if delivery_fees_result else 0.0

    # Tips (from non-cancelled orders)
    tips_result = db.query(func.sum(Order.tip)).filter(
        Order.status != OrderStatus.CANCELLED
    ).scalar()
    tips = float(tips_result) if tips_result else 0.0

    total_revenue = food_sales + delivery_fees + tips

    return EarningBreakdownResponse(
        food_sales=food_sales,
        delivery_fees=delivery_fees,
        tips=tips,
        total_revenue=total_revenue
    )

@router.get("/staff-list", response_model=List[StaffListResponse])
def get_staff_list(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get staff list for dashboard"""
    staff_members = db.query(Staff).order_by(Staff.created_at.desc()).limit(limit).all()

    return [
        StaffListResponse(
            id=staff.id,
            name=staff.name,
            location=staff.location,
            role=staff.role,
            profile_pic=staff.profile_pic,
            created_at=staff.created_at
        )
        for staff in staff_members
    ]

@router.get("/top-customers", response_model=List[TopCustomerResponse])
def get_top_customers(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get top customers by spending for dashboard"""
    customers = db.query(Customer).order_by(Customer.total_spent.desc()).limit(limit).all()

    return [
        TopCustomerResponse(
            id=customer.id,
            name=customer.name,
            membership=customer.membership.value if customer.membership else MembershipType.BRONZE.value,
            orders=customer.total_orders,
            total_spent=customer.total_spent,
            profile_pic=customer.profile_pic
        )
        for customer in customers
    ]

def calculate_percentage_change(current: float, previous: float) -> str:
    """Calculate percentage change"""
    if previous == 0:
        return "+0% (30days)" if current > 0 else "0% (30days)"

    change = ((current - previous) / previous) * 100
    sign = "+" if change > 0 else ""
    return f"{sign}{change:.1f}% (30days)"

