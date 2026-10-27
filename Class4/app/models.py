# This file defines database tables using SQLAlchemy ORM


from sqlalchemy import Column, Integer, String, Boolean , TIMESTAMP, text
from database import Base
  

# This class represents a table in PostgreSQL
class Post(Base):

    # Table name inside PostgreSQL
    __tablename__ = "posts"

    # Primary key
    id = Column(Integer, primary_key=True, nullable=False)

    # Post title
    title = Column(String, nullable=False)

    # Whether post is published
    published = Column(Boolean, server_default='True', nullable=False)

    # Post content
    content = Column(String, nullable=False)

    # Creation time
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))