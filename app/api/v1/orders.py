from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
from app.core.database import get_db
from app.models.order import Order, OrderItem, OrderStatus
from app.models.customer import Customer
from app.models.menu import MenuItem
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderItemResponse

router = APIRouter()

def generate_order_number(db: Session) -> str:
    """Generate unique order number"""
    last_order = db.query(Order).order_by(Order.created_at.desc()).first()
    if last_order and last_order.order_number:
        try:
            last_num = int(last_order.order_number.replace('#', ''))
            return f"#{str(last_num + 1).zfill(3)}"
        except:
            pass
    return "#001"

@router.post("/", response_model=OrderResponse)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order"""
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == order_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Calculate total amount
    total_amount = sum(item.price * item.quantity for item in order_data.items)
    total_amount += order_data.delivery_fee + order_data.tip
    
    # Create order
    order_id = str(uuid.uuid4())
    order_number = generate_order_number(db)
    
    order = Order(
        id=order_id,
        order_number=order_number,
        customer_id=order_data.customer_id,
        status=order_data.status,
        amount=total_amount,
        delivery_fee=order_data.delivery_fee,
        tip=order_data.tip,
        location=order_data.location,
        image_url=order_data.image_url,
        payment_method=order_data.payment_method,
        branch=order_data.branch
    )
    db.add(order)
    
    # Create order items
    for item_data in order_data.items:
        # Validate menu_item_id if provided
        menu_item_id = None
        if item_data.menu_item_id:
            menu_item = db.query(MenuItem).filter(MenuItem.id == item_data.menu_item_id).first()
            if menu_item:
                menu_item_id = item_data.menu_item_id
            # If menu_item_id is provided but doesn't exist, set to None (allow custom items)
            # This allows orders with custom items not in the menu
        
        order_item = OrderItem(
            id=str(uuid.uuid4()),
            order_id=order_id,
            menu_item_id=menu_item_id,  # Will be None if menu_item doesn't exist
            item_name=item_data.item_name,
            quantity=item_data.quantity,
            price=item_data.price,
            additional_data=item_data.additional_data
        )
        db.add(order_item)
    
    # Update customer stats
    customer.total_orders += 1
    customer.total_spent += total_amount
    
    db.commit()
    db.refresh(order)
    
    return get_order(order_id, db)

@router.get("/", response_model=List[OrderResponse])
def get_orders(
    status: Optional[OrderStatus] = Query(None),
    customer_id: Optional[str] = Query(None),
    branch: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all orders with optional filters"""
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    if branch:
        query = query.filter(Order.branch == branch)
    
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    return [format_order_response(order) for order in orders]

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, db: Session = Depends(get_db)):
    """Get order by ID"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return format_order_response(order)

@router.patch("/{order_id}", response_model=OrderResponse)
def update_order(order_id: str, order_update: OrderUpdate, db: Session = Depends(get_db)):
    """Update order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    update_data = order_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    # Recalculate total if amount-related fields changed
    if any(field in update_data for field in ['delivery_fee', 'tip']):
        items_total = sum(item.price * item.quantity for item in order.order_items)
        order.amount = items_total + order.delivery_fee + order.tip
    
    db.commit()
    db.refresh(order)
    return format_order_response(order)

@router.delete("/{order_id}")
def delete_order(order_id: str, db: Session = Depends(get_db)):
    """Delete order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update customer stats
    customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
    if customer:
        customer.total_orders = max(0, customer.total_orders - 1)
        customer.total_spent = max(0, customer.total_spent - order.amount)
    
    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully"}

def format_order_response(order: Order) -> OrderResponse:
    """Format order response with customer name"""
    # Combine order items into a single items string for frontend compatibility
    items_string = ', '.join([item.item_name for item in order.order_items])
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        customer_id=order.customer_id,
        customer_name=order.customer.name if order.customer else "Unknown",
        status=order.status,
        amount=order.amount,
        delivery_fee=order.delivery_fee,
        tip=order.tip,
        location=order.location,
        image_url=order.image_url,
        review_rating=order.review_rating,
        payment_method=order.payment_method,
        branch=order.branch,
        created_at=order.created_at,
        updated_at=order.updated_at,
        order_items=[
            OrderItemResponse(
                id=item.id,
                order_id=item.order_id,
                menu_item_id=item.menu_item_id,
                item_name=item.item_name,
                quantity=item.quantity,
                price=item.price,
                additional_data=item.additional_data,
                created_at=item.created_at
            ) for item in order.order_items
        ],
        items=items_string  # Add items string for frontend
    )

