from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class ComponentSchema(BaseModel):
    name: str
    price: Optional[float] = None

class MenuItemCreate(BaseModel):
    name: str
    category_id: str
    price: float
    description: Optional[str] = None
    image: Optional[str] = None
    status: str = "Available"
    main_components: Optional[List[Dict]] = None
    spicy_elements: Optional[List[str]] = None
    additional_flavor: Optional[List[Dict]] = None
    optional_add_ons: Optional[List[Dict]] = None

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    image: Optional[str] = None
    status: Optional[str] = None
    main_components: Optional[List[Dict]] = None
    spicy_elements: Optional[List[str]] = None
    additional_flavor: Optional[List[Dict]] = None
    optional_add_ons: Optional[List[Dict]] = None

class MenuItemResponse(BaseModel):
    id: str
    name: str
    category_id: str
    category_name: str
    price: float
    description: Optional[str]
    image: Optional[str]
    status: str
    main_components: Optional[List[Dict]]
    spicy_elements: Optional[List[str]]
    additional_flavor: Optional[List[Dict]]
    optional_add_ons: Optional[List[Dict]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class MenuSectionItemCreate(BaseModel):
    menu_item_id: str
    display_order: int = 0

class MenuSectionCreate(BaseModel):
    name: str
    items: Optional[List[MenuSectionItemCreate]] = None

class MenuSectionResponse(BaseModel):
    id: str
    name: str
    items: List[MenuItemResponse]
    created_at: datetime
    
    class Config:
        from_attributes = True

