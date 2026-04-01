from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime, timedelta
from math import ceil
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.security import generate_uuid
from app.models.order import Order, OrderItem, OrderTracking
from app.models.user import User, Address, CartItem, Notification
from app.models.menu import MenuItem
from sqlalchemy import and_
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Request Models
class OrderItemRequest(BaseModel):
    productId: str
    quantity: int
    price: float
    customizations: Optional[Dict] = None
    addOns: Optional[List[Dict]] = None

class CreateOrderRequest(BaseModel):
    items: List[OrderItemRequest]
    addressId: Optional[str] = None
    deliveryType: str = "delivery"  # 'delivery' or 'pickup'
    paymentMethod: str = "cash"
    promoCode: Optional[str] = None
    note: Optional[str] = None
    subtotal: float
    deliveryFee: float
    platformFee: float
    gst: float
    promoDiscount: float = 0.0
    total: float

class CancelOrderRequest(BaseModel):
    reason: Optional[str] = "Cancelled by customer"

def generate_order_number(db: Session) -> str:
    """Generate unique order number"""
    from datetime import datetime
    year = datetime.now().year
    last_order = db.query(Order).filter(
        Order.order_number.like(f"ORD-{year}-%")
    ).order_by(Order.created_at.desc()).first()
    
    if last_order and last_order.order_number:
        try:
            last_num = int(last_order.order_number.split("-")[-1])
            return f"ORD-{year}-{str(last_num + 1).zfill(3)}"
        except:
            pass
    return f"ORD-{year}-001"

@router.post("/")
async def create_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create order from cart or items"""
    try:
        logger.info(f"Creating order for user: {current_user.id} ({current_user.email}), items: {len(request.items)}")
        logger.info(f"Request data: addressId={request.addressId}, deliveryType={request.deliveryType}")
        # Handle address based on delivery type and availability
        address = None
        address_data = None

        if request.addressId:
            # For pickup orders, fetch addresses from database
            if request.deliveryType.lower() == 'pickup':
                # Ensure we always use the system pickup user
                system_user = db.query(User).filter(User.email == "system@shawarma.local").first()
                if not system_user:
                    system_user = db.query(User).filter(User.id == "system-user-pickup").first()
                if not system_user:
                    system_user = User(
                        id="system-user-pickup",
                        name="System",
                        email="system@shawarma.local",
                        is_admin=True
                    )
                    db.add(system_user)
                    db.flush()

                pickup_id_aliases = {
                    "1": "dha-phase-4",
                    "2": "main-pia-road",
                    "3": "lake-city",
                }
                requested_pickup_id = pickup_id_aliases.get(request.addressId, request.addressId)

                # Fetch pickup address from database
                logger.info(f"About to query database for address {requested_pickup_id} with user {system_user.id}")
                pickup_address = db.query(Address).filter(
                    Address.id == requested_pickup_id,
                    Address.user_id == system_user.id
                ).first()
                logger.info(f"Query result: {pickup_address}")

                if not pickup_address:
                    # Auto-create known pickup addresses if seeds were not applied
                    predefined_pickups = {
                        "dha-phase-4": {
                            "name": "DHA Phase 4",
                            "address": "Building # 157, DHA Phase 4 Sector CCA Dha Phase 4, Lahore, 52000",
                            "latitude": 31.4697,
                            "longitude": 74.2728,
                        },
                        "main-pia-road": {
                            "name": "Main PIA Road",
                            "address": "39D, Main PIA Commercial Road, Block D Pia Housing Scheme, Lahore, 54770",
                            "latitude": 31.5204,
                            "longitude": 74.3528,
                        },
                        "lake-city": {
                            "name": "Lake City",
                            "address": "1160 Street 44, Block M 3 A Lake City, Lahore",
                            "latitude": 31.4833,
                            "longitude": 74.3833,
                        },
                    }
                    fallback = predefined_pickups.get(requested_pickup_id)
                    if fallback:
                        pickup_address = Address(
                            id=requested_pickup_id,
                            user_id=system_user.id,
                            name=fallback["name"],
                            address=fallback["address"],
                            latitude=fallback["latitude"],
                            longitude=fallback["longitude"],
                            type="pickup",
                            is_default=False
                        )
                        db.add(pickup_address)
                        db.flush()
                    else:
                        # Last fallback: use first available pickup address
                        pickup_address = db.query(Address).filter(
                            Address.user_id == system_user.id,
                            Address.type == "pickup"
                        ).first()
                        if not pickup_address:
                            raise HTTPException(
                                status_code=status.HTTP_404_NOT_FOUND,
                                detail="Pickup address not found"
                            )

                address_data = {
                    'id': pickup_address.id,
                    'name': pickup_address.name,
                    'address': pickup_address.address
                }

                # Create a mock address object for pickup orders
                class MockAddress:
                    def __init__(self, data):
                        self.id = data['id']
                        self.name = data['name']
                        self.address = data['address']

                address = MockAddress(address_data)
            else:
                # For delivery orders, verify address exists in database
                address = db.query(Address).filter(
                    Address.id == request.addressId,
                    Address.user_id == current_user.id
                ).first()

                if not address:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Address not found"
                    )

                address_data = {
                    'id': address.id,
                    'name': address.name,
                    'address': address.address
                }
        else:
            # No address provided - create a default mock address for orders without location
            logger.info("No address provided - creating order without address")
            address_data = {
                'id': None,
                'name': 'No Address',
                'address': 'Order placed without address'
            }

            class MockAddress:
                def __init__(self, data):
                    self.id = data['id']
                    self.name = data['name']
                    self.address = data['address']

            address = MockAddress(address_data)

        # Create order
        order_id = generate_uuid()
        order_number = generate_order_number(db)
        print(f"[DEBUG] Generated order_id: {order_id}, order_number: {order_number}")

        # Calculate estimated delivery time (30-40 minutes from now)
        estimated_delivery = datetime.utcnow() + timedelta(minutes=35)
        print(f"[DEBUG] Estimated delivery: {estimated_delivery}")

        print(f"[DEBUG] Creating order object...")

        order = Order(
            id=order_id,
            order_number=order_number,
            user_id=current_user.id,
            address_id=address.id if address and hasattr(address, "id") else request.addressId,
            delivery_type=request.deliveryType,
            payment_method=request.paymentMethod,
            payment_status="pending",
            promo_code=request.promoCode,
            promo_discount=request.promoDiscount,
            subtotal=request.subtotal,
            delivery_fee=request.deliveryFee,
            platform_fee=request.platformFee,
            gst=request.gst,
            total=request.total,
            note=request.note,
            status="pending",
            estimated_delivery_time=estimated_delivery
        )

        db.add(order)
        db.flush()

        # Create order items
        order_items_list = []
        for item_data in request.items:
            print(f"[DEBUG] Looking up product: {item_data.productId}")
            product = db.query(MenuItem).filter(MenuItem.id == item_data.productId).first()
            print(f"[DEBUG] Product found: {product.name if product else 'NOT FOUND'}")

            if not product:
                print(f"[ERROR] Product not found: {item_data.productId}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product not found: {item_data.productId}"
                )

            order_item = OrderItem(
                id=generate_uuid(),
                order_id=order_id,
                menu_item_id=item_data.productId,
                item_name=product.name,
                quantity=item_data.quantity,
                price=item_data.price,
                additional_data=json.dumps({
                    "customizations": item_data.customizations,
                    "addOns": item_data.addOns
                }) if item_data.customizations or item_data.addOns else None
            )
            db.add(order_item)
            order_items_list.append(order_item)

        # Create initial tracking
        tracking = OrderTracking(
            id=generate_uuid(),
            order_id=order_id,
            status="pending",
            message="Order placed"
        )
        db.add(tracking)

        # Notify customer that order has been placed
        customer_notification = Notification(
            id=generate_uuid(),
            user_id=current_user.id,
            type="order_status",
            title="Your order has been placed",
            message=f"Order {order_number} has been placed successfully.",
            data=json.dumps({
                "orderId": order_id,
                "orderNumber": order_number,
                "status": "pending"
            })
        )
        db.add(customer_notification)

        # Notify all admin users about new order
        admin_users = db.query(User).filter(User.is_admin == True).all()
        for admin_user in admin_users:
            admin_notification = Notification(
                id=generate_uuid(),
                user_id=admin_user.id,
                type="new_order",
                title="New order received",
                message=f"New order {order_number} placed by {current_user.name or current_user.email or 'customer'}",
                data=json.dumps({
                    "orderId": order_id,
                    "orderNumber": order_number,
                    "customerId": current_user.id,
                    "customerName": current_user.name,
                    "total": request.total,
                    "status": "pending"
                })
            )
            db.add(admin_notification)

        print(f"[DEBUG] About to commit order: {order_id}")
        print(f"[DEBUG] Order object before commit: id={order.id}, number={order.order_number}")
        print(f"[DEBUG] Order items count: {len(order_items_list)}")

        logger.info(f"Starting commit...")
        try:
            db.commit()
            logger.info(f"Order committed successfully: {order_id}")
        except Exception as commit_error:
            logger.error(f"Commit failed: {repr(commit_error)}")
            logger.error(f"Commit error type: {type(commit_error).__name__}")
            db.rollback()
            raise commit_error

        db.refresh(order)
        print(f"[DEBUG] Order refreshed, status: {order.status}, total items: {len(order.order_items) if order.order_items else 0}")

        # Verify data was actually stored
        verify_order = db.query(Order).filter(Order.id == order_id).first()
        if verify_order:
            print(f"[DEBUG] Verification: Order exists in DB with {len(verify_order.order_items) if verify_order.order_items else 0} items")
        else:
            print(f"[ERROR] Verification failed: Order not found in DB after commit!")

        # Return order details
        return {
            "id": order.id,
            "orderNumber": order.order_number,
            "status": order.status,
            "items": [
                {
                    "id": item.id,
                    "productId": item.menu_item_id,
                    "productName": item.item_name,
                    "quantity": item.quantity,
                    "price": item.price,
                    "image": item.menu_item.image if item.menu_item else None
                }
                for item in order_items_list
            ],
            "address": {
                "id": address.id,
                "name": address.name,
                "address": address.address
            } if address and hasattr(address, 'id') and address.id else None,
            "deliveryType": order.delivery_type,
            "paymentMethod": order.payment_method,
            "subtotal": order.subtotal,
            "deliveryFee": order.delivery_fee,
            "platformFee": order.platform_fee,
            "gst": order.gst,
            "promoDiscount": order.promo_discount,
            "total": order.total,
            "note": order.note,
            "createdAt": order.created_at.isoformat() if order.created_at else None,
            "estimatedDeliveryTime": order.estimated_delivery_time.isoformat() if order.estimated_delivery_time else None
        }
    except Exception as e:
        error_msg = str(e) if str(e) else "Unknown error (empty string)"
        print(f"[ERROR] Failed to create order: {error_msg}")
        print(f"[ERROR] Exception type: {type(e).__name__}")
        print(f"[ERROR] Exception repr: {repr(e)}")
        import traceback
        traceback.print_exc()

        # If it's already an HTTPException, re-raise it
        if isinstance(e, HTTPException):
            raise e

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {error_msg}"
        )

@router.get("/")
async def get_orders(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all user orders"""
    query = db.query(Order).filter(Order.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    total = query.count()
    offset = (page - 1) * limit
    orders = query.order_by(Order.created_at.desc()).offset(offset).limit(limit).all()
    
    orders_list = []
    for order in orders:
        orders_list.append({
            "id": order.id,
            "orderNumber": order.order_number,
            "status": order.status,
            "items": [
                {
                    "productId": item.menu_item_id,
                    "productName": item.item_name,
                    "quantity": item.quantity,
                    "price": item.price,
                    "image": item.menu_item.image if item.menu_item else None
                }
                for item in order.order_items[:3]  # Show first 3 items
            ],
            "total": order.total,
            "createdAt": order.created_at.isoformat() if order.created_at else None,
            "estimatedDeliveryTime": order.estimated_delivery_time.isoformat() if order.estimated_delivery_time else None
        })
    
    return {
        "orders": orders_list,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": ceil(total / limit) if total > 0 else 0
        }
    }

@router.get("/{order_id}")
async def get_order_details(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get order details"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    address = order.delivery_address

    # For pickup orders, use hardcoded pickup addresses if address_id is not None
    delivery_address_data = None
    if address:
        delivery_address_data = {
            "id": address.id,
            "name": address.name,
            "address": address.address,
            "latitude": address.latitude,
            "longitude": address.longitude
        }
    elif order.delivery_type.lower() == 'pickup' and order.address_id:
        # Handle pickup orders by fetching from database
        from app.models.user import User
        system_user = db.query(User).filter(User.email == "system@shawarma.local").first()
        if system_user:
            pickup_address_db = db.query(Address).filter(
                and_(Address.id == order.address_id, Address.user_id == system_user.id)
            ).first()
            if pickup_address_db:
                delivery_address_data = {
                    'id': pickup_address_db.id,
                    'name': pickup_address_db.name,
                    'address': pickup_address_db.address,
                    'latitude': pickup_address_db.latitude,
                    'longitude': pickup_address_db.longitude
                }

    # Get tracking
    tracking_list = db.query(OrderTracking).filter(
        OrderTracking.order_id == order_id
    ).order_by(OrderTracking.created_at).all()

    return {
        "id": order.id,
        "orderNumber": order.order_number,
        "status": order.status,
        "items": [
            {
                "id": item.id,
                "productId": item.menu_item_id,
                "productName": item.item_name,
                "quantity": item.quantity,
                "price": item.price,
                "image": item.menu_item.image if item.menu_item else None,
                "customizations": json.loads(item.additional_data).get("customizations") if item.additional_data else None,
                "addOns": json.loads(item.additional_data).get("addOns") if item.additional_data else None
            }
            for item in order.order_items
        ],
        "deliveryAddress": delivery_address_data,
        "deliveryType": order.delivery_type,
        "paymentMethod": order.payment_method,
        "paymentStatus": order.payment_status,
        "subtotal": order.subtotal,
        "deliveryFee": order.delivery_fee,
        "platformFee": order.platform_fee,
        "gst": order.gst,
        "promoDiscount": order.promo_discount,
        "total": order.total,
        "note": order.note,
        "createdAt": order.created_at.isoformat() if order.created_at else None,
        "estimatedDeliveryTime": order.estimated_delivery_time.isoformat() if order.estimated_delivery_time else None,
        "tracking": [
            {
                "status": track.status,
                "timestamp": track.created_at.isoformat() if track.created_at else None,
                "message": track.message
            }
            for track in tracking_list
        ]
    }

@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    request: CancelOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel order"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if order can be cancelled
    if order.status in ["delivered", "cancelled", "out_for_delivery"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order cannot be cancelled at this stage"
        )

    # Allow cancellation only within first 2 minutes after order placement
    if order.created_at:
        elapsed_seconds = (datetime.utcnow() - order.created_at.replace(tzinfo=None)).total_seconds()
        if elapsed_seconds > 120:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order can only be cancelled within 2 minutes of placement"
            )
    
    order.status = "cancelled"
    
    # Add tracking
    tracking = OrderTracking(
        id=generate_uuid(),
        order_id=order_id,
        status="cancelled",
        message=f"Order cancelled: {request.reason or 'Cancelled by customer'}"
    )
    db.add(tracking)

    # Notify customer about cancellation
    customer_notification = Notification(
        id=generate_uuid(),
        user_id=current_user.id,
        type="order_status",
        title="Your order has been cancelled",
        message=f"Order {order.order_number or order.id} has been cancelled.",
        data=json.dumps({
            "orderId": order.id,
            "orderNumber": order.order_number,
            "status": "cancelled"
        })
    )
    db.add(customer_notification)

    # Notify all admin users that order has been cancelled
    admin_users = db.query(User).filter(User.is_admin == True).all()
    for admin_user in admin_users:
        admin_notification = Notification(
            id=generate_uuid(),
            user_id=admin_user.id,
            type="order_cancelled",
            title="Order cancelled",
            message=f"Order {order.order_number or order.id} has been cancelled by customer.",
            data=json.dumps({
                "orderId": order.id,
                "orderNumber": order.order_number,
                "customerId": current_user.id,
                "status": "cancelled"
            })
        )
        db.add(admin_notification)
    
    db.commit()
    
    return {
        "message": "Order cancelled successfully",
        "orderId": order.id,
        "status": order.status
    }

@router.get("/{order_id}/track")
async def track_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track order"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Get tracking
    tracking_list = db.query(OrderTracking).filter(
        OrderTracking.order_id == order_id
    ).order_by(OrderTracking.created_at).all()
    
    return {
        "orderId": order.id,
        "status": order.status,
        "estimatedArrival": order.estimated_delivery_time.isoformat() if order.estimated_delivery_time else None,
        "tracking": [
            {
                "status": track.status,
                "timestamp": track.created_at.isoformat() if track.created_at else None,
                "message": track.message
            }
            for track in tracking_list
        ]
    }

@router.post("/{order_id}/reorder")
async def reorder(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reorder from previous order"""
    old_order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not old_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Create new order with same items
    # This is a simplified version - in production, you'd add items to cart instead
    new_order_id = generate_uuid()
    new_order_number = generate_order_number(db)
    estimated_delivery = datetime.utcnow() + timedelta(minutes=35)
    
    new_order = Order(
        id=new_order_id,
        order_number=new_order_number,
        user_id=current_user.id,
        address_id=old_order.address_id,
        delivery_type=old_order.delivery_type,
        payment_method=old_order.payment_method,
        payment_status="pending",
        subtotal=old_order.subtotal,
        delivery_fee=old_order.delivery_fee,
        platform_fee=old_order.platform_fee,
        gst=old_order.gst,
        total=old_order.total,
        status="pending",
        estimated_delivery_time=estimated_delivery
    )
    
    db.add(new_order)
    db.flush()
    
    # Copy order items
    for old_item in old_order.order_items:
        new_item = OrderItem(
            id=generate_uuid(),
            order_id=new_order_id,
            menu_item_id=old_item.menu_item_id,
            item_name=old_item.item_name,
            quantity=old_item.quantity,
            price=old_item.price,
            additional_data=old_item.additional_data
        )
        db.add(new_item)
    
    # Add tracking
    tracking = OrderTracking(
        id=generate_uuid(),
        order_id=new_order_id,
        status="pending",
        message=f"Order re-placed from {old_order.order_number or old_order.id}"
    )
    db.add(tracking)

    # Notify customer about reorder
    customer_notification = Notification(
        id=generate_uuid(),
        user_id=current_user.id,
        type="order_status",
        title="Your order has been re-placed",
        message=f"Order {new_order_number} has been placed again successfully.",
        data=json.dumps({
            "orderId": new_order_id,
            "orderNumber": new_order_number,
            "sourceOrderId": old_order.id,
            "status": "pending"
        })
    )
    db.add(customer_notification)

    # Notify all admins about reorder
    admin_users = db.query(User).filter(User.is_admin == True).all()
    for admin_user in admin_users:
        admin_notification = Notification(
            id=generate_uuid(),
            user_id=admin_user.id,
            type="order_reordered",
            title="Order placed again",
            message=f"Customer {current_user.name or current_user.email or current_user.id} reordered as {new_order_number}.",
            data=json.dumps({
                "orderId": new_order_id,
                "orderNumber": new_order_number,
                "sourceOrderId": old_order.id,
                "sourceOrderNumber": old_order.order_number,
                "customerId": current_user.id,
                "status": "pending"
            })
        )
        db.add(admin_notification)
    
    db.commit()
    db.refresh(new_order)
    
    return {
        "id": new_order.id,
        "orderNumber": new_order.order_number,
        "message": "Order created successfully from previous order",
        "items": [
            {
                "productId": item.menu_item_id,
                "quantity": item.quantity,
                "price": item.price
            }
            for item in new_order.order_items
        ],
        "total": new_order.total
    }

