from sqlalchemy.orm import Session
from .models import User, Mall, Camera, Customer
from .schemas.user import UserResponse
from passlib.context import CryptContext
import logging

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CRUD operations for User
def create_user(db: Session, user_data):
    try:
        logger.info("Creating new user...")
        # Hash the password
        hashed_password = pwd_context.hash(user_data["password"])
        user_data["password"] = hashed_password
        
        db_user = User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Convert to UserResponse to ensure proper field handling
        return UserResponse.model_validate(db_user)
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        db.rollback()
        raise

def get_user(db: Session, user_id: int):
    try:
        logger.info(f"Fetching user with ID: {user_id}")
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            logger.warning(f"User {user_id} not found")
            return None
        return db_user
    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}")
        raise

def get_user_by_email(db: Session, email: str):
    try:
        logger.info(f"Fetching user with email: {email}")
        return db.query(User).filter(User.email == email).first()
    except Exception as e:
        logger.error(f"Error fetching user by email: {str(e)}")
        raise

def check_user_mall_status(db: Session, user_id: int):
    try:
        logger.info(f"Checking mall status for user {user_id}")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User {user_id} not found")
            return None
        return {
            "has_mall": user.mall_id is not None,
            "mall_id": user.mall_id
        }
    except Exception as e:
        logger.error(f"Error checking mall status: {str(e)}")
        raise

def update_user(db: Session, user_id: int, user_data: dict):
    try:
        logger.info("\n=== DATABASE UPDATE OPERATION ===")
        logger.info(f"Updating user ID: {user_id}")
        logger.info(f"Update data received: {user_data}")
        
        # Get the user
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            error_msg = f"User {user_id} not found in database"
            logger.error(f"ERROR: {error_msg}")
            raise Exception({"message": error_msg, "code": "USER_NOT_FOUND"})

        logger.info("\nCurrent data in database:")
        logger.info(f"Name: {db_user.name}")
        logger.info(f"Email: {db_user.email}")

        # Validate update data
        if not user_data:
            error_msg = "No update data provided"
            logger.error(f"ERROR: {error_msg}")
            raise Exception({"message": error_msg, "code": "NO_UPDATE_DATA"})

        # Update each field
        logger.info("\nUpdating fields:")
        updated_fields = []
        invalid_fields = []
         
        # Convert SQLAlchemy model to dict for comparison
        current_data = {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "mall_id": db_user.mall_id,
            "created_at": db_user.created_at
        }
        
        for key, value in user_data.items():
            if hasattr(db_user, key):
                old_value = getattr(db_user, key)
                # Only update if the value is actually different
                if old_value != value:
                    setattr(db_user, key, value)
                    updated_fields.append(f"{key}: '{old_value}' -> '{value}'")
                    logger.info(f"- {key}: '{old_value}' -> '{value}'")
            else:
                invalid_fields.append(key)
                logger.warning(f"- Warning: Skipping invalid field '{key}'")

        if not updated_fields:
            error_msg = f"No valid fields to update. Invalid fields: {', '.join(invalid_fields)}"
            logger.error(f"ERROR: {error_msg}")
            raise Exception({"message": error_msg, "code": "NO_VALID_FIELDS"})

        try:
            logger.info("\nCommitting changes to database...")
            db.commit()
            db.refresh(db_user)
            
            logger.info("\nVerifying changes...")
            logger.info(f"Updated Name: {db_user.name}")
            logger.info(f"Updated Email: {db_user.email}")
            
            # Convert updated user to dict for response
            updated_data = {
                "id": db_user.id,
                "name": db_user.name,
                "email": db_user.email,
                "mall_id": db_user.mall_id,
                "created_at": db_user.created_at
            }
            
            logger.info("=== UPDATE OPERATION COMPLETE ===\n")
            return updated_data
            
        except Exception as commit_error:
            error_msg = f"Database commit error: {str(commit_error)}"
            logger.error(f"\nERROR: {error_msg}")
            db.rollback()
            logger.info("Changes rolled back")
            raise Exception({"message": error_msg, "code": "DATABASE_ERROR"})

    except Exception as e:
        if len(e.args) > 0 and isinstance(e.args[0], dict):
            # If we already have a structured error, re-raise it
            raise
        else:
            # Otherwise, create a structured error
            error_msg = str(e)
            logger.error(f"\nERROR: {error_msg}")
            db.rollback()
            logger.info("Changes rolled back")
            raise Exception({"message": error_msg, "code": "DATABASE_ERROR"})

def delete_user(db: Session, user_id: int):
    try:
        logger.info(f"Attempting to delete user {user_id}")
        # Get the user
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            logger.warning(f"User {user_id} not found")
            return None

        # If user has a mall, delete it first
        if db_user.mall:
            logger.info(f"Deleting associated mall for user {user_id}")
            db.delete(db_user.mall)
            db.commit()

        # Delete the user
        logger.info(f"Deleting user {user_id}")
        db.delete(db_user)
        db.commit()
        logger.info(f"Successfully deleted user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        db.rollback()
        return None

# CRUD operations for Mall
def create_mall(db: Session, mall_data):
    db_mall = Mall(**mall_data)
    db.add(db_mall)
    db.commit()
    db.refresh(db_mall)
    return db_mall

def get_mall(db: Session, mall_id: int):
    return db.query(Mall).filter(Mall.id == mall_id).first()

def update_mall(db: Session, mall_id: int, mall_data):
    db_mall = db.query(Mall).filter(Mall.id == mall_id).first()
    for key, value in mall_data.items():
        setattr(db_mall, key, value)
    db.commit()
    db.refresh(db_mall)
    return db_mall

def delete_mall(db: Session, mall_id: int):
    try:
        db_mall = db.query(Mall).filter(Mall.id == mall_id).first()
        if not db_mall:
            return None
            
        # Get the owner user
        owner = db_mall.owner
        if owner:
            # Clear the mall_id from the user
            owner.mall_id = None
            
        # Delete the mall
        db.delete(db_mall)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting mall: {str(e)}")
        return None

# CRUD operations for Camera
def create_camera(db: Session, camera_data):
    db_camera = Camera(**camera_data)
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera

def get_camera(db: Session, camera_id: int):
    return db.query(Camera).filter(Camera.id == camera_id).first()

def get_cameras_by_mall(db: Session, mall_id: int):
    return db.query(Camera).filter(Camera.mall_id == mall_id).all()

def update_camera(db: Session, camera_id: int, camera_data: dict):
    try:
        logger.info(f"=== Starting database update for camera {camera_id} ===")
        
        # Get the camera
        db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
        if not db_camera:
            logger.error(f"Camera {camera_id} not found in database")
            return None

        logger.info(f"Current database camera data: {db_camera.__dict__}")
        logger.info(f"Update data received: {camera_data}")

        # Track what fields are being updated
        updated_fields = []
        
        # Update each field
        for key, value in camera_data.items():
            if hasattr(db_camera, key):
                old_value = getattr(db_camera, key)
                setattr(db_camera, key, value)
                updated_fields.append(f"{key}: {old_value} -> {value}")
                logger.info(f"Updated field {key}")
            else:
                logger.warning(f"Skipping invalid field: {key}")

        logger.info(f"Fields updated: {', '.join(updated_fields)}")

        # Commit the changes
        try:
            logger.info("Committing changes to database...")
            db.commit()
            db.refresh(db_camera)
            logger.info("Successfully committed changes")
            logger.info(f"Updated camera data in DB: {db_camera.__dict__}")
        except Exception as e:
            logger.error(f"Error committing camera update: {str(e)}")
            db.rollback()
            logger.info("Rolled back changes due to error")
            raise e

        logger.info(f"=== Successfully completed database update for camera {camera_id} ===")
        return db_camera
    except Exception as e:
        logger.error(f"Error in update_camera: {str(e)}")
        db.rollback()
        logger.info("Rolled back changes due to error")
        raise e

def delete_camera(db: Session, camera_id: int):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    db.delete(db_camera)
    db.commit()

# CRUD operations for Customer
def create_customer(db: Session, customer_data):
    db_customer = Customer(**customer_data)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def get_customer(db: Session, customer_id: int):
    return db.query(Customer).filter(Customer.id == customer_id).first()

def update_customer(db: Session, customer_id: int, customer_data):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    for key, value in customer_data.items():
        setattr(db_customer, key, value)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def delete_customer(db: Session, customer_id: int):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    db.delete(db_customer)
    db.commit()