from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.core.database import get_db
from app.models.menu import Category

router = APIRouter()

# Response Models
class CategoryResponse(BaseModel):
    id: str
    name: str
    icon: str = ""
    image: str = ""

@router.get("/")
def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    try:
        categories = db.query(Category).all()
        print(f"[Categories API] Found {len(categories)} categories")

        return {
            "categories": [
                {
                    "id": cat.id,
                    "name": cat.name,
                    "icon": cat.icon or "",
                    "image": cat.image or ""
                }
                for cat in categories
            ]
        }
    except Exception as e:
        print(f"[Categories API] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"categories": []}
