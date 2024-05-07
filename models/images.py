from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config.db import Base

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String(36), ForeignKey('scans.scan_id'))
    image_path = Column(String(255))
    prediction = Column(String(36), default="")
    scan = relationship("Scan", back_populates="images")
