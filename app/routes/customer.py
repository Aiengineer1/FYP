from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas.customer import CustomerCreate, CustomerResponse
from ..crud import create_customer, get_customer, update_customer, delete_customer
from ..database import get_db

router = APIRouter()

@router.post("/add_customer", response_model=CustomerResponse)
def add_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    return create_customer(db, customer)

@router.get("/{customer_id}", response_model=CustomerResponse)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = get_customer(db, customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer_route(customer_id: int, customer: CustomerCreate, db: Session = Depends(get_db)):
    db_customer = update_customer(db, customer_id, customer)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@router.delete("/{customer_id}")
def delete_customer_route(customer_id: int, db: Session = Depends(get_db)):
    # Check if customer exists first
    db_customer = get_customer(db, customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    delete_customer(db, customer_id)
    return {"detail": "Customer deleted"}
