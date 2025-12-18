from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from app.core.database import get_db
from app.models.staff import Staff, StaffRole, StaffStatus
from app.models.role import Role
from app.schemas.staff import StaffCreate, StaffUpdate, StaffResponse

router = APIRouter()

def string_to_role(role_str: str) -> StaffRole:
    """Convert string to StaffRole enum"""
    role_mapping = {
        'MANAGER': StaffRole.MANAGER,
        'Manager': StaffRole.MANAGER,
        'manager': StaffRole.MANAGER,
        'CHEF': StaffRole.CHEF,
        'Chef': StaffRole.CHEF,
        'chef': StaffRole.CHEF,
        'RIDER': StaffRole.RIDER,
        'Rider': StaffRole.RIDER,
        'rider': StaffRole.RIDER,
        'CASHIER': StaffRole.CASHIER,
        'Cashier': StaffRole.CASHIER,
        'cashier': StaffRole.CASHIER,
    }
    return role_mapping.get(role_str.strip(), StaffRole.MANAGER)

def string_to_status(status_str: str) -> StaffStatus:
    """Convert string to StaffStatus enum"""
    status_mapping = {
        'ON_DUTY': StaffStatus.ON_DUTY,
        'ON-DUTY': StaffStatus.ON_DUTY,
        'On-Duty': StaffStatus.ON_DUTY,
        'on-duty': StaffStatus.ON_DUTY,
        'OFF_DUTY': StaffStatus.OFF_DUTY,
        'OFF DUTY': StaffStatus.OFF_DUTY,
        'Off Duty': StaffStatus.OFF_DUTY,
        'off duty': StaffStatus.OFF_DUTY,
    }
    return status_mapping.get(status_str.strip(), StaffStatus.ON_DUTY)


@router.post("/", response_model=StaffResponse)
def create_staff(staff_data: StaffCreate, db: Session = Depends(get_db)):
    """Create a new staff member"""
    staff_id = str(uuid.uuid4())
    
    # Convert enum values to strings for database storage
    staff_dict = staff_data.dict()
    
    # Convert role enum to string value
    if 'role' in staff_dict:
        if isinstance(staff_dict['role'], StaffRole):
            staff_dict['role'] = staff_dict['role'].value  # Convert enum to string
        elif isinstance(staff_dict['role'], str):
            # If it's a string, convert to enum first, then to string value
            role_enum = string_to_role(staff_dict['role'])
            staff_dict['role'] = role_enum.value
    
    # Convert status enum to string value
    if 'status' in staff_dict:
        if isinstance(staff_dict['status'], StaffStatus):
            staff_dict['status'] = staff_dict['status'].value  # Convert enum to string
        elif isinstance(staff_dict['status'], str):
            # If it's a string, convert to enum first, then to string value
            status_enum = string_to_status(staff_dict['status'])
            staff_dict['status'] = status_enum.value
    else:
        staff_dict['status'] = StaffStatus.ON_DUTY.value  # Default value
    
    # Validate role_id if provided
    role_id = staff_dict.get('role_id')
    if role_id:
        # Check if role exists in roles table
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            # If role_id is provided but doesn't exist, set to None
            staff_dict['role_id'] = None
    else:
        staff_dict['role_id'] = None
    
    staff = Staff(
        id=staff_id,
        **staff_dict
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    
    # Pydantic will convert string values to enums via validators in StaffResponse
    return staff

@router.get("/", response_model=List[StaffResponse])
def get_staff(
    role: Optional[StaffRole] = Query(None),
    location: Optional[str] = Query(None),
    status: Optional[StaffStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all staff with optional filters"""
    query = db.query(Staff)
    
    # Filter by role (compare string values)
    if role:
        query = query.filter(Staff.role == role.value)
    if location:
        query = query.filter(Staff.location == location)
    # Filter by status (compare string values)
    if status:
        query = query.filter(Staff.status == status.value)
    
    staff_list = query.order_by(Staff.created_at.desc()).offset(skip).limit(limit).all()
    
    # Pydantic will convert string values to enums via validators in StaffResponse
    return staff_list

@router.get("/{staff_id}", response_model=StaffResponse)
def get_staff_member(staff_id: str, db: Session = Depends(get_db)):
    """Get staff member by ID"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Pydantic will convert string values to enums via validators in StaffResponse
    return staff

@router.patch("/{staff_id}", response_model=StaffResponse)
def update_staff(staff_id: str, staff_update: StaffUpdate, db: Session = Depends(get_db)):
    """Update staff member"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    update_data = staff_update.dict(exclude_unset=True)
    
    # Convert enum values to strings for database storage
    if 'role' in update_data:
        if isinstance(update_data['role'], StaffRole):
            update_data['role'] = update_data['role'].value  # Convert enum to string
        elif isinstance(update_data['role'], str):
            # If it's a string, convert to enum first, then to string value
            role_enum = string_to_role(update_data['role'])
            update_data['role'] = role_enum.value
    
    if 'status' in update_data:
        if isinstance(update_data['status'], StaffStatus):
            update_data['status'] = update_data['status'].value  # Convert enum to string
        elif isinstance(update_data['status'], str):
            # If it's a string, convert to enum first, then to string value
            status_enum = string_to_status(update_data['status'])
            update_data['status'] = status_enum.value
    
    # Validate role_id if provided
    if 'role_id' in update_data:
        role_id = update_data['role_id']
        if role_id:
            # Check if role exists in roles table
            role = db.query(Role).filter(Role.id == role_id).first()
            if not role:
                # If role_id is provided but doesn't exist, set to None
                update_data['role_id'] = None
        else:
            update_data['role_id'] = None
    
    for field, value in update_data.items():
        setattr(staff, field, value)
    
    db.commit()
    db.refresh(staff)
    
    # Pydantic will convert string values to enums via validators in StaffResponse
    return staff

@router.delete("/{staff_id}")
def delete_staff(staff_id: str, db: Session = Depends(get_db)):
    """Delete staff member"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    db.delete(staff)
    db.commit()
    return {"message": "Staff member deleted successfully"}

