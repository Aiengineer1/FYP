from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

# Customers Table (Tracking Mall Visitors)
class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    mall_id = Column(Integer, ForeignKey("malls.id", ondelete="CASCADE"), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)
    trolley_id = Column(String, nullable=True)
    trolley_sub_id = Column(String, nullable=True)
    routes = Column(JSON, nullable=True)
    interactions = Column(JSON, nullable=True)
    visited_zones = Column(JSON, nullable=True)
    mall = relationship("Mall", back_populates="customers")
