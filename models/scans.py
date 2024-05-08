from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from config.db import Base

class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String(36), unique=True, index=True)
    has_alzheimer = Column(Boolean, default=False)
    alzheimer_percent = Column(String(36), default="")
    images = relationship("Image", back_populates="scan")
