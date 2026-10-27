from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from random import randrange

# Database related imports
import psycopg2
from psycopg2.extras import RealDictCursor
import time

# SQLAlchemy (ORM)
from sqlalchemy.orm import Session

# Local files
import models,schemas, utils 
from database import engine, get_db

from routers import post,user 


app = FastAPI()   #Initializing FastAPI app
models.Base.metadata.create_all(bind=engine)   #Creating tables in the database based on the models defined in models.py Uses SQLAlchemy's create_all method to create tables based on the metadata defined in the models. The bind=engine argument specifies the database connection to use for creating the tables.




# MANUAL DATABASE CONNECTION (psycopg2)

while True:
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='fastapi',
            user='postgres',
            password='shrinidhiNK@01',
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        print("Database connection was successful")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error:", error)
        time.sleep(2)

# TEMPORARY DATA (FOR TESTING)
my_posts = [
    {"title": "title 1", "content": "content 1", "id": 1},
    {"title": "title 2", "content": "content 2", "id": 2}
]

app.include_router(post.router)
app.include_router(user.router)

# ROOT ENDPOINT
@app.get("/")
def root():
    return {"Message": "Hello World"}


