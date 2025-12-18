from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.role import Role, Permission, role_permission_table

router = APIRouter()

@router.get("/permissions")
def get_permissions(db: Session = Depends(get_db)):
    """Get all available permissions"""
    permissions = db.query(Permission).all()
    return permissions

@router.get("/roles")
def get_roles(db: Session = Depends(get_db)):
    """Get all roles with their permissions"""
    roles = db.query(Role).all()
    return roles

