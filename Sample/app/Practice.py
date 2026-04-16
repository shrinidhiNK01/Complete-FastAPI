from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from typing import Optional
from psycopg2.extras import RealDictCursor
import psycopg2
import time

app = FastAPI()

# Pydantic Model
class Post(BaseModel):
    title: str
    content: str
    published: bool = True


# Database Connection
while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapi",
            user="postgres",
            password="shrinidhiNK@01",
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        print("Database connection successful")
        break

    except Exception as error:
        print("Database connection failed")
        print("Error:", error)
        time.sleep(2)


# Root Endpoint
@app.get("/")
def root():
    return {"message": "Hello World"}


# Get All Posts
@app.get("/posts", status_code=status.HTTP_200_OK)
def get_posts():

    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()

    return {"data": posts}


# Create Post
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):

    cursor.execute(
        """INSERT INTO posts (title, content, published)
        VALUES (%s,%s,%s)
        RETURNING *""",
        (post.title, post.content, post.published)
    )

    new_post = cursor.fetchone()
    conn.commit()

    return {"data": new_post}


# Get Latest Post
@app.get("/posts/latest")
def get_latest_post():

    cursor.execute("""SELECT * FROM posts ORDER BY id DESC LIMIT 1""")
    post = cursor.fetchone()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No posts found"
        )

    return {"data": post}


# Get Post by ID
@app.get("/posts/{id}")
def get_post(id: int):

    cursor.execute(
        """SELECT * FROM posts WHERE id = %s""",
        (str(id),)
    )

    post = cursor.fetchone()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} was not found"
        )

    return {"data": post}


# Delete Post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):

    cursor.execute(
        """DELETE FROM posts WHERE id = %s RETURNING *""",
        (str(id),)
    )

    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} was not found"
        )

    return {"message": "Post deleted successfully"}


# Update Post
@app.put("/posts/{id}")
def update_post(id: int, post: Post):

    cursor.execute(
        """UPDATE posts
        SET title=%s, content=%s, published=%s
        WHERE id=%s
        RETURNING *""",
        (post.title, post.content, post.published, str(id))
    )

    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} was not found"
        )

    return {"data": updated_post}