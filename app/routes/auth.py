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
    try:
        logger.info(f"Processing login request for email: {user.email}")
        
        # Get user from database
        db_user = get_user_by_email(db, user.email)
        if not db_user:
            logger.warning(f"Login failed: User {user.email} not found")
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        # Verify password
        if not pwd_context.verify(user.password, db_user.password):
            logger.warning(f"Login failed: Invalid password for {user.email}")
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        logger.info(f"User authenticated successfully: {db_user.email}")
        
        # Create JWT token with frontend-expected payload format
        from datetime import datetime, timedelta
        token_data = {
            "user_id": db_user.id,
            "email": db_user.email,
            "name": db_user.name,
            "mall_id": db_user.mall_id,
            "sub": db_user.email,  # Standard JWT claim
            "exp": datetime.utcnow() + timedelta(days=30)  # 30 days instead of 24 hours
        }
        access_token = create_access_token(data=token_data)
        
        # Return response in exact format expected by frontend
        response = {
            "access_token": access_token,
            "user_id": db_user.id,
            "name": db_user.name, 
            "email": db_user.email,
            "mall_id": db_user.mall_id
        }
        
        logger.info(f"Login successful for user: {db_user.email}")
        return response
        
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "An unexpected error occurred", "code": "LOGIN_ERROR"}
        )

@router.get("/check-mall/{user_id}", response_model=MallStatusResponse)
def check_mall_status(user_id: int, db: Session = Depends(get_db)):
    status = check_user_mall_status(db, user_id)
    if status is None:
        raise HTTPException(status_code=404, detail="User not found")
    return status

@router.get("/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify JWT token and return user data for frontend AuthInitializer"""
    try:
        return {
            "valid": True,
            "user": {
                "user_id": current_user["id"],
                "name": current_user["name"],
                "email": current_user["email"], 
                "mall_id": current_user["mall_id"]
            }
        }
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=401, 
            detail={"valid": False, "message": "Invalid token"}
        )

@router.post("/refresh-token")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh/extend the JWT token expiration time"""
    try:
        logger.info(f"Refreshing token for user: {current_user['email']}")
        
        # Create new token with extended expiration
        from datetime import datetime, timedelta
        token_data = {
            "user_id": current_user["id"],
            "email": current_user["email"],
            "name": current_user["name"],
            "mall_id": current_user["mall_id"],
            "sub": current_user["email"],
            "exp": datetime.utcnow() + timedelta(days=30)  # 30 days
        }
        new_access_token = create_access_token(data=token_data)
        
        logger.info(f"Token refreshed successfully for user: {current_user['email']}")
        
        return {
            "access_token": new_access_token,
            "user_id": current_user["id"],
            "name": current_user["name"], 
            "email": current_user["email"],
            "mall_id": current_user["mall_id"],
            "message": "Token refreshed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to refresh token", "code": "REFRESH_FAILED"}
        )

@router.delete("/user/{user_id}")
def delete_user_route(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a specific user and their associated mall.
    Only admin users or the user themselves can delete accounts.
    """
    try:
        # Check if user is trying to delete their own account or is admin
        if current_user["id"] != user_id:
            # For now, allow only self-deletion. Add admin check here if needed
            raise HTTPException(
                status_code=403, 
                detail="You can only delete your own account"
            )
        
        logger.info(f"User {current_user['id']} requesting account deletion")
        
        result = delete_user(db, user_id)
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"User {user_id} and associated mall deleted successfully")
        return {
            "success": True,
            "message": "Account and associated mall deleted successfully",
            "user_id": user_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete account")

@router.delete("/account/delete")
def delete_my_account(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete the current user's account and associated mall.
    This is a convenience endpoint for users to delete their own account.
    """
    try:
        user_id = current_user["id"]
        logger.info(f"User {user_id} requesting self-account deletion")
        
        result = delete_user(db, user_id)
        if result is None:
            raise HTTPException(status_code=404, detail="User account not found")
        
        logger.info(f"User {user_id} successfully deleted their account")
        return {
            "success": True,
            "message": "Your account and associated mall have been deleted successfully",
            "user_id": user_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user account {current_user['id']}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete your account")

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