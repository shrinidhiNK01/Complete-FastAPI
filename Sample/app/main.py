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
import models,schemas
from database import engine, get_db

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

# ROOT ENDPOINT
@app.get("/")
def root():
    return {"Message": "Hello World"}

# # SQLALCHEMY TEST ENDPOINT :- Uses ORM instead of raw SQL
# @app.get("/sqlalchemy")
# def test_posts(db: Session = Depends(get_db)):   #injects DB session into the endpoint function using FastAPI's dependency injection system. The get_db function is defined in the database module and is responsible for creating and managing the database session.
#     posts = db.query(models.Post).all()
#     return {"data": posts}

# GET ALL POSTS :- Fetches all posts from DB, Uses SQLAlchemy
@app.get("/posts", status_code=status.HTTP_200_OK, response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

# CREATE POST :- Creates a new post in the DB, Uses SQLAlchemy
@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

# GET LATEST POST (FROM LIST) - Uses local list, not DB
@app.get("/posts/latest")
def get_latest_post():
    post = my_posts[len(my_posts) - 1]
    return {"detail": post}

# HELPER FUNCTION
def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p
    return None

# GET SINGLE POST (psycopg2)
@app.get("/posts/{id}",response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):

    # cursor.execute('SELECT * FROM "Posts" WHERE id=%s', (str(id),))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id==id).first()
    print(post)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        )

    return {"Post details": post}

# DELETE POST
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):  #database session is injected into the endpoint function using FastAPI's dependency injection system. The get_db function is defined in the database module and is responsible for creating and managing the database session.

    # Manual SQL Vode
    # cursor.execute('DELETE FROM "Posts" WHERE id=%s RETURNING *', (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    deleted_post = db.query(models.Post).filter(models.Post.id == id).first()

    if deleted_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        )
    db.delete(deleted_post)
    db.commit()
    return {"message": f"post with id: {id} was successfully deleted"}

# UPDATE POST
@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostUpdate, db: Session = Depends(get_db)):

    # cursor.execute(
    #     'UPDATE "Posts" SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *',
    #     (post.title, post.content, post.published, id)
    # )

    # updated_post = cursor.fetchone()
    # conn.commit()
    updated_post = db.query(models.Post).filter(models.Post.id == id).first()

    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        )
    # manually assign fields
    updated_post.title = post.title
    updated_post.content = post.content
    updated_post.published = post.published

    db.commit()
    db.refresh(updated_post)
    return {"data": updated_post}

##############################==New ENDPOINTS FOR USER CREATION==##############################

@app.post("/users",status_code=status.HTTP_200_OK)
def CreateUser(user: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"data": new_user}
    

