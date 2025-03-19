from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

# Users Table (Mall Owner)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # Hashed password
    mall_id = Column(Integer, ForeignKey("malls.id", ondelete="SET NULL"), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    mall = relationship("Mall", back_populates="owner", uselist=False, cascade="all, delete", single_parent=True)
