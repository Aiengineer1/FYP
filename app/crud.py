from sqlalchemy.orm import Session
from .models import User, Mall, Camera, Customer

# CRUD operations for User
def create_user(db: Session, user_data):
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def check_user_mall_status(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    return {
        "has_mall": user.mall_id is not None,
        "mall_id": user.mall_id
    }

def update_user(db: Session, user_id: int, user_data):
    db_user = db.query(User).filter(User.id == user_id).first()
    for key, value in user_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    try:
        # Get the user
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None

        # If user has a mall, delete it first
        if db_user.mall:
            db.delete(db_user.mall)
            db.commit()

        # Delete the user
        db.delete(db_user)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error deleting user: {str(e)}")
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
        print(f"Error deleting mall: {str(e)}")
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

def update_camera(db: Session, camera_id: int, camera_data):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    for key, value in camera_data.items():
        setattr(db_camera, key, value)
    db.commit()
    db.refresh(db_camera)
    return db_camera

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
