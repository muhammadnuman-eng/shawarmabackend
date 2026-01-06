from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.core.location_service import get_google_maps_service, LocationServiceError

router = APIRouter()

@router.get("/location/reverse-geocode")
async def reverse_geocode(
    lat: float = Query(..., alias="lat", description="Latitude coordinate"),
    lng: float = Query(..., alias="lng", description="Longitude coordinate"),
    db: Session = Depends(get_db)
):
    """
    Get address from coordinates (reverse geocoding)

    Uses Google Maps API to convert latitude/longitude to human-readable address
    """
    try:
        location_service = get_google_maps_service()
        result = location_service.reverse_geocode(lat, lng)
        return result
    except LocationServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Location service error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/location/geocode")
async def geocode(
    address: str = Query(..., alias="address", description="Address to geocode"),
    db: Session = Depends(get_db)
):
    """
    Get coordinates from address (geocoding)

    Uses Google Maps API to convert address to latitude/longitude coordinates
    """
    try:
        location_service = get_google_maps_service()
        result = location_service.geocode(address)
        return result
    except LocationServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Location service error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

