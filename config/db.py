from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.keys import encoded_host, encoded_name, encoded_password, encoded_user

SQLALCHEMY_DATABASE_URL = f"postgresql://{encoded_user}:{encoded_password}@{encoded_host}/{encoded_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
