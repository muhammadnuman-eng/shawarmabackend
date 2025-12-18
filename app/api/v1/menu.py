from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from app.core.database import get_db
from app.models.menu import MenuItem, Category, MenuSection, MenuSectionItem
from app.schemas.menu import (
    MenuItemCreate, MenuItemUpdate, MenuItemResponse,
    CategoryCreate, CategoryResponse,
    MenuSectionCreate, MenuSectionResponse
)

router = APIRouter()

# Categories
@router.post("/categories", response_model=CategoryResponse)
def create_category(category_data: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category"""
    # Check if category already exists
    existing = db.query(Category).filter(Category.name == category_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    category_id = str(uuid.uuid4())
    category = Category(
        id=category_id,
        **category_data.dict()
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    categories = db.query(Category).order_by(Category.name).all()
    return categories

@router.delete("/categories/{category_id}")
def delete_category(category_id: str, db: Session = Depends(get_db)):
    """Delete category"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}

# Menu Items
@router.post("/items", response_model=MenuItemResponse)
def create_menu_item(item_data: MenuItemCreate, db: Session = Depends(get_db)):
    """Create a new menu item"""
    # Verify category exists
    category = db.query(Category).filter(Category.id == item_data.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    item_id = str(uuid.uuid4())
    menu_item = MenuItem(
        id=item_id,
        **item_data.dict()
    )
    db.add(menu_item)
    db.commit()
    db.refresh(menu_item)
    return format_menu_item_response(menu_item)

@router.get("/items", response_model=List[MenuItemResponse])
def get_menu_items(
    category_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all menu items"""
    query = db.query(MenuItem)
    
    if category_id:
        query = query.filter(MenuItem.category_id == category_id)
    if status:
        query = query.filter(MenuItem.status == status)
    
    items = query.order_by(MenuItem.created_at.desc()).offset(skip).limit(limit).all()
    return [format_menu_item_response(item) for item in items]

@router.get("/items/{item_id}", response_model=MenuItemResponse)
def get_menu_item(item_id: str, db: Session = Depends(get_db)):
    """Get menu item by ID"""
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return format_menu_item_response(menu_item)

@router.patch("/items/{item_id}", response_model=MenuItemResponse)
def update_menu_item(item_id: str, item_update: MenuItemUpdate, db: Session = Depends(get_db)):
    """Update menu item"""
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(menu_item, field, value)
    
    db.commit()
    db.refresh(menu_item)
    return format_menu_item_response(menu_item)

@router.delete("/items/{item_id}")
def delete_menu_item(item_id: str, db: Session = Depends(get_db)):
    """Delete menu item"""
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    db.delete(menu_item)
    db.commit()
    return {"message": "Menu item deleted successfully"}

# Menu Sections
@router.post("/sections", response_model=MenuSectionResponse)
def create_menu_section(section_data: MenuSectionCreate, db: Session = Depends(get_db)):
    """Create a new menu section"""
    section_id = str(uuid.uuid4())
    section = MenuSection(
        id=section_id,
        name=section_data.name
    )
    db.add(section)
    
    # Add items to section
    if section_data.items:
        for idx, item_data in enumerate(section_data.items):
            # Validate menu_item_id if provided
            menu_item_id = None
            if item_data.menu_item_id:
                menu_item = db.query(MenuItem).filter(MenuItem.id == item_data.menu_item_id).first()
                if menu_item:
                    menu_item_id = item_data.menu_item_id
                # If menu_item_id is provided but doesn't exist, skip this item
                # (don't add invalid menu items to section)
            
            if menu_item_id:  # Only add if valid menu_item_id
                section_item = MenuSectionItem(
                    id=str(uuid.uuid4()),
                    section_id=section_id,
                    menu_item_id=menu_item_id,
                    display_order=item_data.display_order or idx
                )
                db.add(section_item)
    
    db.commit()
    db.refresh(section)
    return format_section_response(section, db)

@router.get("/sections", response_model=List[MenuSectionResponse])
def get_menu_sections(db: Session = Depends(get_db)):
    """Get all menu sections"""
    sections = db.query(MenuSection).order_by(MenuSection.created_at.desc()).all()
    return [format_section_response(section, db) for section in sections]

@router.get("/sections/{section_id}", response_model=MenuSectionResponse)
def get_menu_section(section_id: str, db: Session = Depends(get_db)):
    """Get menu section by ID"""
    section = db.query(MenuSection).filter(MenuSection.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Menu section not found")
    return format_section_response(section, db)

@router.delete("/sections/{section_id}")
def delete_menu_section(section_id: str, db: Session = Depends(get_db)):
    """Delete menu section"""
    section = db.query(MenuSection).filter(MenuSection.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Menu section not found")
    
    db.delete(section)
    db.commit()
    return {"message": "Menu section deleted successfully"}

def format_menu_item_response(item: MenuItem) -> MenuItemResponse:
    """Format menu item response with category name"""
    return MenuItemResponse(
        id=item.id,
        name=item.name,
        category_id=item.category_id,
        category_name=item.category.name if item.category else "Unknown",
        price=item.price,
        description=item.description,
        image=item.image,
        status=item.status,
        main_components=item.main_components,
        spicy_elements=item.spicy_elements,
        additional_flavor=item.additional_flavor,
        optional_add_ons=item.optional_add_ons,
        created_at=item.created_at,
        updated_at=item.updated_at
    )

def format_section_response(section: MenuSection, db: Session) -> MenuSectionResponse:
    """Format menu section response with items"""
    section_items = db.query(MenuSectionItem).filter(
        MenuSectionItem.section_id == section.id
    ).order_by(MenuSectionItem.display_order).all()
    
    items = []
    for section_item in section_items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == section_item.menu_item_id).first()
        if menu_item:
            items.append(format_menu_item_response(menu_item))
    
    return MenuSectionResponse(
        id=section.id,
        name=section.name,
        items=items,
        created_at=section.created_at
    )

