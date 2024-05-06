from sqlalchemy import Column, Integer, String, ForeignKey # type: ignore
from sqlalchemy.orm import relationship # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.exc import ProgrammingError # type: ignore
from config.db import engine

Base = declarative_base()

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String(36), ForeignKey('scans.scan_id'))
    image_path = Column(String(255))
    prediction = Column(String(36), default="")
    scan = relationship("Scan", back_populates="images")


# Create database tables
try:
    Base.metadata.create_all(bind=engine)
except ProgrammingError as e:
    raise RuntimeError(f"Error creating database tables: {e}")
