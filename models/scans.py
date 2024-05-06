from sqlalchemy import Column, Integer, String, Boolean # type: ignore
from sqlalchemy.orm import relationship # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.exc import ProgrammingError # type: ignore
from config.db import engine

Base = declarative_base()

# Define database models
class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String(36), unique=True, index=True)
    has_alzheimer = Column(Boolean, default=False)
    images = relationship("Image", back_populates="scan")

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
except ProgrammingError as e:
    raise RuntimeError(f"Error creating database tables: {e}")
