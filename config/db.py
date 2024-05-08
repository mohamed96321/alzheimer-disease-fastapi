from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from structlog import get_logger
from config.keys import encoded_host, encoded_name, encoded_password, encoded_user

logger = get_logger()
SQLALCHEMY_DATABASE_URL = f"postgresql://{encoded_user}:{encoded_password}@{encoded_host}/{encoded_name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def create_database_tables(Base):
    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as e:
        logger.error(f"Error creating database tables: {e}")
        raise RuntimeError("Failed to create database tables")