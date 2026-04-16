from pydantic import BaseModel ,EmailStr
from datetime import datetime
from typing import Optional, List
#Defining a Pydantic model for the Post data. This model will be used for data validation and serialization when creating or updating posts.
class PostBase(BaseModel):     #REQUEST BODY SCHEMA (Pydantic Model)
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass
class PostUpdate(PostBase):
    pass
class Post(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    created_at:Optional[datetime]  
    class config:
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
