from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from starlette.responses import Response
from ..schemas.mall import MallCreate, MallResponse, MallResponseWithImage
from ..crud import create_mall, get_mall, update_mall, delete_mall, get_user, update_user
from ..database import get_db
from ..dependencies import get_current_user
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/mall",
    tags=["mall"]
)

@router.post("/create", response_model=MallResponse)
async def create_new_mall(
    name: str,
    address: str,
    user_id: int,
    map_image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Check if user exists
        user = get_user(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user already has a mall
        if user.mall_id is not None:
            raise HTTPException(status_code=400, detail="User already has a mall")
        
        # Read and validate map image
        map_image_data = await map_image.read()
        if not map_image_data:
            raise HTTPException(status_code=400, detail="Map image is required")
        
        # Validate image size (max 5MB)
        if len(map_image_data) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Map image size should be less than 5MB")
        
        # Validate image type
        if not map_image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Prepare mall data
        mall_data = {
            "name": name,
            "address": address,
            "map_image": map_image_data
        }
        
        # Create the mall
        new_mall = create_mall(db=db, mall_data=mall_data)
        
        # Update user with new mall_id
        update_user(db=db, user_id=user_id, user_data={"mall_id": new_mall.id})
        
        return new_mall
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error creating mall: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{mall_id}", response_model=MallResponse)
def read_mall(
    mall_id: int, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        db_mall = get_mall(db, mall_id)
        if db_mall is None:
            raise HTTPException(status_code=404, detail="Mall not found")
        return db_mall
    except Exception as e:
        logger.error(f"Error fetching mall: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{mall_id}/image")
async def get_mall_image(
    mall_id: int, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        db_mall = get_mall(db, mall_id)
        if db_mall is None:
            raise HTTPException(status_code=404, detail="Mall not found")
        if not db_mall.map_image:
            raise HTTPException(status_code=404, detail="Mall map image not found")
        return Response(content=db_mall.map_image, media_type="image/jpeg")
    except Exception as e:
        logger.error(f"Error fetching mall image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{mall_id}", response_model=MallResponse)
async def update_mall_route(
    mall_id: int,
    name: Optional[str] = None,
    address: Optional[str] = None,
    contact_email: Optional[str] = None,
    contact_number: Optional[str] = None,
    map_image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Get existing mall
        db_mall = get_mall(db, mall_id)
        if db_mall is None:
            raise HTTPException(status_code=404, detail="Mall not found")
        
        # Prepare update data
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if address is not None:
            update_data["address"] = address
        if contact_email is not None:
            update_data["contact_email"] = contact_email
        if contact_number is not None:
            update_data["contact_number"] = contact_number
        if map_image:
            map_image_data = await map_image.read()
            if map_image_data:
                update_data["map_image"] = map_image_data
        
        updated_mall = update_mall(db, mall_id, update_data)
        return updated_mall
    except Exception as e:
        logger.error(f"Error updating mall: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{mall_id}")
def delete_mall_route(
    mall_id: int, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        mall = get_mall(db, mall_id)
        if mall is None:
            raise HTTPException(status_code=404, detail="Mall not found")
        delete_mall(db, mall_id)
        return {"detail": "Mall deleted"}
    except Exception as e:
        logger.error(f"Error deleting mall: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{mall_id}/setup", response_model=MallResponse)
async def setup_mall(
    mall_id: int,
    name: Optional[str] = None,
    address: Optional[str] = None,
    contact_email: Optional[str] = None,
    contact_number: Optional[str] = None,
    map_image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Setup or configure a mall with initial settings.
    This endpoint allows updating basic mall information and map.
    """
    try:
        # Get existing mall
        db_mall = get_mall(db, mall_id)
        if db_mall is None:
            raise HTTPException(status_code=404, detail="Mall not found")
        
        # Prepare setup data
        setup_data = {}
        if name is not None:
            setup_data["name"] = name
        if address is not None:
            setup_data["address"] = address
        if contact_email is not None:
            setup_data["contact_email"] = contact_email
        if contact_number is not None:
            setup_data["contact_number"] = contact_number
        if map_image:
            map_image_data = await map_image.read()
            if map_image_data:
                setup_data["map_image"] = map_image_data
        
        # Update mall with setup data
        updated_mall = update_mall(db, mall_id, setup_data)
        return updated_mall
    except Exception as e:
        logger.error(f"Error setting up mall: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
