from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas.user import UserCreate, UserResponse, UserLogin, MallStatusResponse, LoginResponse, UserUpdate
from ..crud import create_user, get_user_by_email, check_user_mall_status, delete_user, update_user, get_user
from ..database import get_db
from passlib.context import CryptContext
from ..dependencies import create_access_token, get_current_user
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Processing signup request for email: {user.email}")
        
        # Check if user exists
        db_user = get_user_by_email(db, user.email)
        if db_user:
            logger.warning(f"Signup failed: Email {user.email} already registered")
            raise HTTPException(
                status_code=400,
                detail={"message": "Email already registered", "code": "EMAIL_EXISTS"}
            )
        
        # Create new user
        logger.info("Creating new user...")
        try:
            new_user = create_user(db=db, user_data=user.model_dump())
            logger.info(f"User created successfully with ID: {new_user.id}")
            return new_user
        except Exception as create_error:
            logger.error(f"Error creating user: {str(create_error)}")
            raise HTTPException(
                status_code=500,
                detail={"message": "Failed to create user account", "code": "CREATE_FAILED"}
            )
            
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f"Unexpected error during signup: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "An unexpected error occurred", "code": "UNEXPECTED_ERROR"}
        )

@router.post("/login", response_model=LoginResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Create access token
    access_token = create_access_token(data={"sub": db_user.email})
    
    # Create response with both id and user_id
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        id=db_user.id,
        user_id=db_user.id,  # Set both id and user_id
        email=db_user.email,
        name=db_user.name,
        mall_id=db_user.mall_id,
        created_at=db_user.created_at
    )

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

@router.get("/user/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Fetching profile for user ID: {current_user['id']}")
        db_user = get_user(db, current_user["id"])
        if not db_user:
            logger.error(f"User {current_user['id']} not found in database")
            raise HTTPException(status_code=404, detail="User not found")
        
        # Convert to Pydantic model to ensure proper field handling
        return UserResponse.model_validate(db_user)
    except Exception as e:
        logger.error(f"Error fetching user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/user/update", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        logger.info("\n=== USER UPDATE REQUEST ===")
        logger.info(f"Current user ID: {current_user['id']}")
        logger.info(f"Received update data: {user_data.model_dump()}")
        
        # Get current user from database
        db_user = get_user(db, current_user["id"])
        if not db_user:
            error_msg = f"User {current_user['id']} not found in database"
            logger.error(f"ERROR: {error_msg}")
            raise HTTPException(
                status_code=404,
                detail={"message": error_msg, "code": "USER_NOT_FOUND"}
            )
        
        logger.info("\nCurrent user data in database:")
        logger.info(f"Name: {db_user.name}")
        logger.info(f"Email: {db_user.email}")
        
        # Prepare update data
        update_data = user_data.model_dump(exclude_unset=True)
        if not update_data:
            error_msg = "No valid fields provided for update"
            logger.error(f"ERROR: {error_msg}")
            raise HTTPException(
                status_code=400,
                detail={"message": error_msg, "code": "NO_UPDATE_DATA"}
            )
            
        logger.info("\nProcessing update with data:")
        logger.info(update_data)
        
        # If password is being updated, hash it
        if "password" in update_data:
            logger.info("Hashing new password...")
            update_data["password"] = pwd_context.hash(update_data["password"])
        
        try:
            logger.info("\nAttempting to update user in database...")
            updated_user_dict = update_user(db, current_user["id"], update_data)
            
            logger.info("\nUpdate successful! Converting to response model...")
            # Convert to Pydantic model to ensure proper field handling
            response = UserResponse.model_validate(updated_user_dict)
            
            logger.info("New user data:")
            logger.info(f"Name: {response.name}")
            logger.info(f"Email: {response.email}")
            logger.info("=== UPDATE COMPLETE ===\n")
            
            return response
            
        except Exception as update_err:
            if len(update_err.args) > 0 and isinstance(update_err.args[0], dict):
                error_data = update_err.args[0]
                logger.error(f"Structured error: {error_data}")
                raise HTTPException(
                    status_code=500,
                    detail=error_data
                )
            else:
                error_msg = str(update_err)
                logger.error(f"Unstructured error: {error_msg}")
                raise HTTPException(
                    status_code=500,
                    detail={"message": error_msg, "code": "DATABASE_ERROR"}
                )
            
    except HTTPException as http_err:
        logger.error(f"HTTP Exception: {http_err.detail}")
        raise http_err
    except Exception as e:
        error_msg = f"Unexpected error during user update: {str(e)}"
        logger.error(f"\nERROR: {error_msg}")
        raise HTTPException(
            status_code=500,
            detail={"message": error_msg, "code": "UNEXPECTED_ERROR"}
        )