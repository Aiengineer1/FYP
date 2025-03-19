from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from ..schemas.mall import MallCreate, MallResponse, MallResponseWithImage
from ..crud import create_mall, get_mall, update_mall, delete_mall, get_user, update_user
from ..database import get_db
from typing import Optional

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
    db: Session = Depends(get_db)
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
        
        # Return mall without image data
        return MallResponse(
            id=new_mall.id,
            name=new_mall.name,
            address=new_mall.address,
            created_at=new_mall.created_at
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error creating mall: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating mall: {str(e)}")

@router.get("/{mall_id}", response_model=MallResponse)
def read_mall(mall_id: int, db: Session = Depends(get_db)):
    db_mall = get_mall(db, mall_id)
    if db_mall is None:
        raise HTTPException(status_code=404, detail="Mall not found")
    return MallResponse(
        id=db_mall.id,
        name=db_mall.name,
        address=db_mall.address,
        created_at=db_mall.created_at
    )

@router.get("/{mall_id}/image")
async def get_mall_image(mall_id: int, db: Session = Depends(get_db)):
    db_mall = get_mall(db, mall_id)
    if db_mall is None:
        raise HTTPException(status_code=404, detail="Mall not found")
    if not db_mall.map_image:
        raise HTTPException(status_code=404, detail="Mall map image not found")
    return Response(content=db_mall.map_image, media_type="image/jpeg")

@router.put("/{mall_id}", response_model=MallResponse)
async def update_mall_route(
    mall_id: int,
    name: Optional[str] = None,
    address: Optional[str] = None,
    map_image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
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
    if map_image:
        map_image_data = await map_image.read()
        if map_image_data:
            update_data["map_image"] = map_image_data
    
    updated_mall = update_mall(db, mall_id, update_data)
    return MallResponse(
        id=updated_mall.id,
        name=updated_mall.name,
        address=updated_mall.address,
        created_at=updated_mall.created_at
    )

@router.delete("/{mall_id}")
def delete_mall_route(mall_id: int, db: Session = Depends(get_db)):
    mall = get_mall(db, mall_id)
    if mall is None:
        raise HTTPException(status_code=404, detail="Mall not found")
    delete_mall(db, mall_id)
    return {"detail": "Mall deleted"}

@router.post("/{mall_id}/setup", response_model=MallResponse)
async def setup_mall(
    mall_id: int,
    name: Optional[str] = None,
    address: Optional[str] = None,
    map_image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """
    Setup or configure a mall with initial settings.
    This endpoint allows updating basic mall information and map.
    """
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
    if map_image:
        map_image_data = await map_image.read()
        if map_image_data:
            setup_data["map_image"] = map_image_data
    
    # Update mall with setup data
    updated_mall = update_mall(db, mall_id, setup_data)
    return MallResponse(
        id=updated_mall.id,
        name=updated_mall.name,
        address=updated_mall.address,
        created_at=updated_mall.created_at
    )
