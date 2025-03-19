from datetime import datetime
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# Malls Table (Mall Information)
class Mall(Base):
    __tablename__ = "malls"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    map_image = Column(LargeBinary, nullable=True)  # Store image data directly
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship("User", back_populates="mall", uselist=False)
    cameras = relationship("Camera", back_populates="mall", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="mall", cascade="all, delete-orphan")
