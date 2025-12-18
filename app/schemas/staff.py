from pydantic import BaseModel, field_validator, Field
from typing import Optional, Union
from datetime import datetime
from app.models.staff import StaffRole, StaffStatus

class StaffCreate(BaseModel):
    name: str
    role: Union[StaffRole, str]  # Accept both enum and string
    location: str
    phone: Optional[str] = None
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    address: Optional[str] = None
    profile_pic: Optional[str] = None
    status: Union[StaffStatus, str] = StaffStatus.ON_DUTY  # Accept both enum and string
    role_id: Optional[str] = None
    
    @field_validator('role', mode='before')
    @classmethod
    def validate_role(cls, v):
        if isinstance(v, str):
            # Map string to enum
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
            return role_mapping.get(v.strip(), StaffRole.MANAGER)
        return v
    
    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        if isinstance(v, str):
            # Map string to enum
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
            return status_mapping.get(v.strip(), StaffStatus.ON_DUTY)
        return v


class StaffUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[Union[StaffRole, str]] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    address: Optional[str] = None
    profile_pic: Optional[str] = None
    status: Optional[Union[StaffStatus, str]] = None
    role_id: Optional[str] = None
    
    @field_validator('role', mode='before')
    @classmethod
    def validate_role(cls, v):
        if isinstance(v, str):
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
            return role_mapping.get(v.strip(), StaffRole.MANAGER)
        return v
    
    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        if isinstance(v, str):
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
            return status_mapping.get(v.strip(), StaffStatus.ON_DUTY)
        return v

class StaffResponse(BaseModel):
    id: str
    name: str
    role: StaffRole
    location: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    profile_pic: Optional[str]
    status: StaffStatus
    role_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    @field_validator('role', mode='before')
    @classmethod
    def validate_role(cls, v):
        if isinstance(v, str):
            # Map string to enum
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
            return role_mapping.get(v.strip() if v else '', StaffRole.MANAGER)
        return v
    
    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        if isinstance(v, str):
            # Map string to enum
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
            return status_mapping.get(v.strip() if v else '', StaffStatus.ON_DUTY)
        return v
    
    class Config:
        from_attributes = True

