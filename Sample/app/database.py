# This file is responsible for:
# 1. Creating the SQLAlchemy engine
# 2. Creating database sessions
# 3. Providing Base class for models
# 4. Providing dependency for FastAPI to access DB

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQL_ALCHEMY_DATABASE_URL = 'postgresql://<username>:<password>@<ip-address/hostname>/<database_name>'

# IMPORTANT:
# Your password contains '@'
# In URL it must be encoded as %40
# shrinidhiNK@01  -> shrinidhiNK%4001

SQL_ALCHEMY_DATABASE_URL = "postgresql://postgres:shrinidhiNK%4001@localhost:5432/fastapi"

# Engine is responsible for talking to the database
engine = create_engine(SQL_ALCHEMY_DATABASE_URL)

# SessionLocal creates a new database session for every request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class used for creating ORM models
Base = declarative_base()


# Dependency used in FastAPI endpoints
# This creates a DB session and closes it after request finishes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()