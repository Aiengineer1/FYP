"""
ID Management Routes
Provides endpoints to monitor and manage ID sequences with gap filling.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.crud import get_all_id_statistics, get_next_available_ids
from app.utils.id_manager import reset_sequence_to_lowest_gap
from app.models import User, Mall, Camera, Customer
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/id-management", tags=["ID Management"])

@router.get("/statistics")
async def get_id_statistics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive ID statistics for all models.
    Shows gaps, efficiency, and next available IDs.
    """
    try:
        logger.info(f"User {current_user['user_id']} requesting ID statistics")
        
        statistics = get_all_id_statistics(db)
        
        return {
            "success": True,
            "message": "ID statistics retrieved successfully",
            "data": statistics,
            "summary": {
                "total_models": len(statistics),
                "models_with_gaps": sum(1 for stats in statistics.values() if stats.get('gap_count', 0) > 0),
                "total_gaps": sum(stats.get('gap_count', 0) for stats in statistics.values()),
                "average_efficiency": round(sum(stats.get('sequence_efficiency', 0) for stats in statistics.values()) / len(statistics), 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting ID statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ID statistics: {str(e)}"
        )

@router.get("/next-available")
async def get_next_available(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the next available ID for each model.
    This shows what ID will be assigned to new records.
    """
    try:
        logger.info(f"User {current_user['user_id']} requesting next available IDs")
        
        next_ids = get_next_available_ids(db)
        
        return {
            "success": True,
            "message": "Next available IDs retrieved successfully",
            "data": next_ids
        }
        
    except Exception as e:
        logger.error(f"Error getting next available IDs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get next available IDs: {str(e)}"
        )

@router.get("/statistics/{model_name}")
async def get_model_statistics(
    model_name: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed ID statistics for a specific model.
    model_name should be one of: user, mall, camera, customer
    """
    try:
        logger.info(f"User {current_user['user_id']} requesting statistics for {model_name}")
        
        # Map model names to classes
        model_map = {
            'user': User,
            'mall': Mall,
            'camera': Camera,
            'customer': Customer
        }
        
        if model_name.lower() not in model_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid model name. Must be one of: {', '.join(model_map.keys())}"
            )
        
        from app.utils.id_manager import get_id_statistics
        model_class = model_map[model_name.lower()]
        statistics = get_id_statistics(db, model_class)
        
        return {
            "success": True,
            "message": f"Statistics for {model_name} retrieved successfully",
            "data": statistics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting {model_name} statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get {model_name} statistics: {str(e)}"
        )

@router.post("/reset-sequence/{model_name}")
async def reset_model_sequence(
    model_name: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reset the auto-increment sequence for a model to the lowest available gap.
    This is useful after bulk deletions to optimize ID reuse.
    model_name should be one of: user, mall, camera, customer
    """
    try:
        logger.info(f"User {current_user['user_id']} requesting sequence reset for {model_name}")
        
        # Map model names to classes
        model_map = {
            'user': User,
            'mall': Mall,
            'camera': Camera,
            'customer': Customer
        }
        
        if model_name.lower() not in model_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid model name. Must be one of: {', '.join(model_map.keys())}"
            )
        
        model_class = model_map[model_name.lower()]
        sequence_value = reset_sequence_to_lowest_gap(db, model_class)
        
        if sequence_value is not None:
            return {
                "success": True,
                "message": f"Sequence for {model_name} reset successfully",
                "data": {
                    "model": model_name,
                    "sequence_reset_to": sequence_value
                }
            }
        else:
            return {
                "success": False,
                "message": f"Could not reset sequence for {model_name}",
                "data": {
                    "model": model_name,
                    "note": "Manual ID management is active"
                }
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting {model_name} sequence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset {model_name} sequence: {str(e)}"
        )

@router.get("/demo/scenario")
async def demonstrate_id_management(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Demonstrate ID management scenario as described by the user.
    Shows what happens when users are created, deleted, and created again.
    """
    try:
        logger.info(f"User {current_user['user_id']} requesting ID management demonstration")
        
        # Get current user statistics
        from app.utils.id_manager import get_id_statistics
        current_stats = get_id_statistics(db, User)
        
        # Create a scenario explanation
        scenario = {
            "current_situation": {
                "total_users": current_stats.get('total_records', 0),
                "min_id": current_stats.get('min_id'),
                "max_id": current_stats.get('max_id'),
                "gaps": current_stats.get('gaps', []),
                "next_new_user_will_get_id": current_stats.get('next_available_id')
            },
            "scenario_explanation": {
                "step_1": "If you have users with IDs [1, 2, 3, ..., 20] and you delete user ID 5",
                "step_2": "Next new user will get ID 5 (filling the gap)",
                "step_3": "If you delete users 5, 10, 15 - gaps will be [5, 10, 15]",
                "step_4": "Next 3 new users will get IDs 5, 10, 15 (in order)",
                "step_5": "If you delete ALL users, next new user will get ID 1",
                "step_6": "This maintains clean, sequential numbering without gaps"
            },
            "benefits": [
                "No gaps in ID sequences",
                "Reuses deleted IDs efficiently", 
                "Maintains chronological order when possible",
                "Optimizes database storage",
                "Clean, predictable ID assignment"
            ]
        }
        
        return {
            "success": True,
            "message": "ID management scenario demonstration",
            "data": scenario
        }
        
    except Exception as e:
        logger.error(f"Error creating demonstration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create demonstration: {str(e)}"
        ) 