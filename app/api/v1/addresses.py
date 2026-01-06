from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.security import generate_uuid
from app.models.user import Address, User

router = APIRouter()

# Request Models
class CreateAddressRequest(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    isDefault: bool = False
    type: str = "home"  # 'home', 'work', 'other'

class UpdateAddressRequest(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    isDefault: Optional[bool] = None
    type: Optional[str] = None

@router.get("/addresses")
async def get_addresses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all user addresses + pickup addresses"""
    # Get user's delivery addresses
    user_addresses = db.query(Address).filter(
        Address.user_id == current_user.id,
        Address.type != "pickup"
    ).all()

    # Get system pickup addresses
    system_user = db.query(User).filter(User.email == "system@shawarma.local").first()
    pickup_addresses = []
    if system_user:
        pickup_addresses = db.query(Address).filter(
            Address.user_id == system_user.id,
            Address.type == "pickup"
        ).all()

    all_addresses = user_addresses + pickup_addresses

    return {
        "addresses": [
            {
                "id": addr.id,
                "name": addr.name,
                "address": addr.address,
                "latitude": addr.latitude,
                "longitude": addr.longitude,
                "isDefault": addr.is_default,
                "type": addr.type
            }
            for addr in all_addresses
        ]
    }

@router.post("/addresses")
async def create_address(
    request: CreateAddressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add new address"""
    # If this is set as default, unset other defaults
    if request.isDefault:
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.is_default == True
        ).update({"is_default": False})
    
    address = Address(
        id=generate_uuid(),
        user_id=current_user.id,
        name=request.name,
        address=request.address,
        latitude=request.latitude,
        longitude=request.longitude,
        is_default=request.isDefault,
        type=request.type
    )
    
    db.add(address)
    db.commit()
    db.refresh(address)
    
    return {
        "id": address.id,
        "name": address.name,
        "address": address.address,
        "latitude": address.latitude,
        "longitude": address.longitude,
        "isDefault": address.is_default,
        "type": address.type,
        "createdAt": address.created_at.isoformat() if address.created_at else None
    }

@router.put("/addresses/{address_id}")
async def update_address(
    address_id: str,
    request: UpdateAddressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update address"""
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    # If setting as default, unset other defaults
    if request.isDefault is not None and request.isDefault:
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.id != address_id,
            Address.is_default == True
        ).update({"is_default": False})
    
    # Update fields
    if request.name is not None:
        address.name = request.name
    if request.address is not None:
        address.address = request.address
    if request.latitude is not None:
        address.latitude = request.latitude
    if request.longitude is not None:
        address.longitude = request.longitude
    if request.isDefault is not None:
        address.is_default = request.isDefault
    if request.type is not None:
        address.type = request.type
    
    db.commit()
    db.refresh(address)
    
    return {
        "id": address.id,
        "name": address.name,
        "address": address.address,
        "latitude": address.latitude,
        "longitude": address.longitude,
        "isDefault": address.is_default,
        "type": address.type,
        "updatedAt": address.updated_at.isoformat() if address.updated_at else None
    }

@router.delete("/addresses/{address_id}")
async def delete_address(
    address_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete address"""
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    db.delete(address)
    db.commit()
    
    return {"message": "Address deleted successfully"}

@router.put("/addresses/{address_id}/default")
async def set_default_address(
    address_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set default address"""
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    # Unset other defaults
    db.query(Address).filter(
        Address.user_id == current_user.id,
        Address.id != address_id,
        Address.is_default == True
    ).update({"is_default": False})
    
    # Set this as default
    address.is_default = True
    db.commit()
    
    return {"message": "Default address updated successfully"}

