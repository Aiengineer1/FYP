from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

# Cameras Table (Mall-Specific Cameras)
class Camera(Base):
    __tablename__ = "cameras"
    id = Column(Integer, primary_key=True, index=True)
    mall_id = Column(Integer, ForeignKey("malls.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)  # Store securely
    location = Column(String, nullable=True)
    homography_map = Column(JSON, nullable=True)
    fov_zones = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    mall = relationship("Mall", back_populates="cameras")
