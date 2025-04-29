from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas.user import UserCreate, UserResponse, UserLogin, MallStatusResponse, LoginResponse
from ..crud import create_user, get_user_by_email, check_user_mall_status, delete_user
from ..database import get_db
from passlib.context import CryptContext
from ..dependencies import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user_data=user.model_dump())

@router.post("/login", response_model=LoginResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Create access token
    access_token = create_access_token(data={"sub": db_user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user.id,
        "email": db_user.email,
        "name": db_user.name,
        "mall_id": db_user.mall_id,
        "created_at": db_user.created_at
    }

@router.get("/check-mall/{user_id}", response_model=MallStatusResponse)
def check_mall_status(user_id: int, db: Session = Depends(get_db)):
    status = check_user_mall_status(db, user_id)
    if status is None:
        raise HTTPException(status_code=404, detail="User not found")
    return status

@router.delete("/user/{user_id}")
def delete_user_route(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user and their associated mall.
    This will cascade delete the mall due to the ondelete="CASCADE" constraint.
    """
    result = delete_user(db, user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User and associated mall deleted successfully"}
