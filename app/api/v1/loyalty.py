from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.security import generate_uuid
from app.models.user import User, LoyaltyPoint, Reward

router = APIRouter()

@router.get("/loyalty/points")
async def get_loyalty_points(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user loyalty points"""
    # Calculate total points
    earned_points = db.query(func.sum(LoyaltyPoint.points)).filter(
        LoyaltyPoint.user_id == current_user.id,
        LoyaltyPoint.type == "earned"
    ).scalar() or 0
    
    used_points = db.query(func.sum(LoyaltyPoint.points)).filter(
        LoyaltyPoint.user_id == current_user.id,
        LoyaltyPoint.type == "used"
    ).scalar() or 0
    
    available_points = earned_points - used_points
    
    # Determine level (simplified)
    level = "Bronze"
    next_level = "Silver"
    points_to_next = 100
    
    if available_points >= 500:
        level = "Gold"
        next_level = "Platinum"
        points_to_next = 500
    elif available_points >= 200:
        level = "Silver"
        next_level = "Gold"
        points_to_next = 300
    
    # Count visits (orders)
    from app.models.order import Order
    visits = db.query(Order).filter(Order.user_id == current_user.id).count()
    
    return {
        "totalPoints": earned_points,
        "availablePoints": available_points,
        "usedPoints": used_points,
        "level": level,
        "nextLevel": next_level,
        "pointsToNextLevel": points_to_next,
        "visits": visits,
        "visitsRequired": 6  # Example
    }

@router.get("/loyalty/rewards")
async def get_rewards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available rewards"""
    rewards = db.query(Reward).filter(Reward.is_available == True).all()
    
    return {
        "rewards": [
            {
                "id": reward.id,
                "name": reward.name,
                "description": reward.description,
                "pointsRequired": reward.points_required,
                "image": reward.image,
                "isAvailable": reward.is_available
            }
            for reward in rewards
        ]
    }

@router.post("/loyalty/rewards/{reward_id}/redeem")
async def redeem_reward(
    reward_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Redeem reward"""
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    
    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reward not found"
        )
    
    if not reward.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reward is not available"
        )
    
    # Check available points
    from sqlalchemy import func
    earned_points = db.query(func.sum(LoyaltyPoint.points)).filter(
        LoyaltyPoint.user_id == current_user.id,
        LoyaltyPoint.type == "earned"
    ).scalar() or 0
    
    used_points = db.query(func.sum(LoyaltyPoint.points)).filter(
        LoyaltyPoint.user_id == current_user.id,
        LoyaltyPoint.type == "used"
    ).scalar() or 0
    
    available_points = earned_points - used_points
    
    if available_points < reward.points_required:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient points"
        )
    
    # Deduct points
    loyalty_point = LoyaltyPoint(
        id=generate_uuid(),
        user_id=current_user.id,
        points=reward.points_required,
        type="used",
        description=f"Redeemed: {reward.name}"
    )
    db.add(loyalty_point)
    db.commit()
    
    return {
        "message": "Reward redeemed successfully",
        "rewardId": reward_id,
        "pointsUsed": reward.points_required,
        "remainingPoints": available_points - reward.points_required
    }

