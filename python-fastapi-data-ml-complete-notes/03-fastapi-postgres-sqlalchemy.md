# 03. FastAPI, PostgreSQL, SQLAlchemy, And Alembic

## 1. What FastAPI Is

FastAPI is a Python framework for building APIs. It uses Python type hints, Pydantic validation, Starlette web features, and automatic OpenAPI documentation.

Use FastAPI when you need:

- REST APIs.
- JSON request/response validation.
- Async support.
- Automatic Swagger docs.
- Dependency injection.
- Production-ready backend services.

## 2. HTTP Basics

HTTP is request-response communication.

```mermaid
sequenceDiagram
  participant Client
  participant API
  Client->>API: GET /posts/1
  API-->>Client: 200 JSON response
```

Common methods:

- `GET`: read.
- `POST`: create.
- `PUT`: replace.
- `PATCH`: partial update.
- `DELETE`: remove.

Common status codes:

- `200 OK`
- `201 Created`
- `204 No Content`
- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `422 Validation Error`
- `500 Internal Server Error`

## 3. Start A FastAPI App

Install:

```bash
python -m pip install "fastapi[standard]"
```

`main.py`:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello API"}
```

Run:

```bash
fastapi dev main.py
```

or:

```bash
uvicorn main:app --reload
```

Line by line:

- `FastAPI()` creates the app object.
- `@app.get("/")` registers a GET route.
- `read_root` runs when the route is requested.
- Returning a dict becomes JSON.

## 4. Path Operations

In FastAPI, a path operation is a route plus HTTP method.

```python
@app.get("/posts/{post_id}")
def get_post(post_id: int) -> dict[str, int]:
    return {"post_id": post_id}
```

`post_id` is a path parameter. Because it is typed as `int`, FastAPI validates and converts it.

If request is:

```txt
GET /posts/123
```

FastAPI passes:

```python
post_id = 123
```

## 5. Route Order Matters

```python
@app.get("/posts/latest")
def get_latest_post():
    return {"post": "latest"}

@app.get("/posts/{post_id}")
def get_post(post_id: int):
    return {"post_id": post_id}
```

Put fixed routes like `/posts/latest` before dynamic routes like `/posts/{post_id}`.

## 6. Query Parameters

```python
@app.get("/posts")
def list_posts(limit: int = 10, offset: int = 0, search: str | None = None):
    return {"limit": limit, "offset": offset, "search": search}
```

Request:

```txt
GET /posts?limit=5&offset=10&search=python
```

## 7. Pydantic Schemas

Pydantic validates request and response data.

```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    email: EmailStr
```

FastAPI uses these models to:

- Validate input.
- Generate OpenAPI docs.
- Serialize responses.
- Show examples in Swagger UI.

## 8. Request Body

```python
from pydantic import BaseModel

class PostCreate(BaseModel):
    title: str
    content: str
    published: bool = True

@app.post("/posts", status_code=201)
def create_post(post: PostCreate):
    return post
```

Line by line:

- `PostCreate` defines expected JSON.
- `published` defaults to `True`.
- FastAPI parses request body into `post`.
- Invalid data returns `422`.

## 9. In-Memory CRUD

```python
posts: list[dict] = []

@app.post("/posts", status_code=201)
def create_post(post: PostCreate):
    new_post = post.model_dump()
    new_post["id"] = len(posts) + 1
    posts.append(new_post)
    return new_post

@app.get("/posts")
def get_posts():
    return posts
```

This is useful for learning, but data disappears when the app restarts.

## 10. PostgreSQL Basics

PostgreSQL is a relational database.

Important concepts:

- Database.
- Schema.
- Table.
- Row.
- Column.
- Primary key.
- Foreign key.
- Index.
- Constraint.

Posts table:

```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    published BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

## 11. SQL Queries

Read all:

```sql
SELECT * FROM posts;
```

Filter:

```sql
SELECT * FROM posts WHERE published = true;
```

Operators:

```sql
SELECT * FROM posts WHERE id IN (1, 2, 3);
SELECT * FROM posts WHERE title LIKE '%python%';
SELECT * FROM posts ORDER BY created_at DESC;
SELECT * FROM posts LIMIT 10 OFFSET 20;
```

Insert:

```sql
INSERT INTO posts (title, content)
VALUES ('FastAPI', 'Build APIs with Python')
RETURNING *;
```

Update:

```sql
UPDATE posts
SET title = 'Updated title'
WHERE id = 1
RETURNING *;
```

Delete:

```sql
DELETE FROM posts
WHERE id = 1;
```

## 12. SQLAlchemy 2.0 Setup

Install:

```bash
python -m pip install sqlalchemy psycopg
```

`database.py`:

```python
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = "postgresql+psycopg://postgres:password@localhost:5432/fastapi_app"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Line by line:

- `create_engine` creates database connection infrastructure.
- `SessionLocal` creates database sessions.
- `Base` is the parent for ORM models.
- `get_db` is a FastAPI dependency.
- `yield` gives the session to the route.
- `finally` closes the session.

## 13. SQLAlchemy Models

`models.py`:

```python
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    posts: Mapped[list["Post"]] = relationship(back_populates="owner")

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    owner: Mapped[User] = relationship(back_populates="posts")
```

Important idea:

- Pydantic models define API shape.
- SQLAlchemy models define database shape.

## 14. CRUD With SQLAlchemy

```python
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    db_post = models.Post(**post.model_dump(), owner_id=1)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post
```

Line by line:

- `Depends(get_db)` asks FastAPI for a database session.
- `post.model_dump()` converts Pydantic model to dict.
- `models.Post(...)` creates ORM object.
- `db.add` stages insert.
- `db.commit` saves transaction.
- `db.refresh` reloads generated fields like `id`.

Read:

```python
@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    return db.query(models.Post).all()
```

Get one:

```python
@app.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(models.Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
```

Delete:

```python
@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(models.Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
```

Update:

```python
@app.put("/posts/{post_id}")
def update_post(post_id: int, updated: schemas.PostCreate, db: Session = Depends(get_db)):
    post = db.get(models.Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    for key, value in updated.model_dump().items():
        setattr(post, key, value)

    db.commit()
    db.refresh(post)
    return post
```

## 15. Response Models

```python
class PostRead(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    owner: UserRead

    model_config = {"from_attributes": True}

@app.get("/posts/{post_id}", response_model=PostRead)
def get_post(post_id: int, db: Session = Depends(get_db)):
    ...
```

`response_model` controls what fields the API returns.

## 16. Routers

Large apps should split routes.

`routers/posts.py`:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.get("/")
def get_posts():
    return []
```

`main.py`:

```python
from fastapi import FastAPI
from .routers import posts

app = FastAPI()
app.include_router(posts.router)
```

Benefits:

- Cleaner `main.py`.
- Feature-based organization.
- Easier testing.

## 17. Relationships And Foreign Keys

A user can own many posts.

```mermaid
erDiagram
  USERS ||--o{ POSTS : owns
  USERS {
    int id
    string email
  }
  POSTS {
    int id
    string title
    int owner_id
  }
```

Foreign key:

```sql
ALTER TABLE posts
ADD CONSTRAINT fk_posts_users
FOREIGN KEY (owner_id)
REFERENCES users(id)
ON DELETE CASCADE;
```

## 18. Votes Table

Many users can vote on many posts. That is a many-to-many relationship.

```sql
CREATE TABLE votes (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, post_id)
);
```

Composite primary key prevents duplicate votes by the same user on the same post.

## 19. Joins

SQL:

```sql
SELECT posts.*, COUNT(votes.post_id) AS votes
FROM posts
LEFT JOIN votes ON posts.id = votes.post_id
GROUP BY posts.id;
```

SQLAlchemy idea:

```python
from sqlalchemy import func

results = (
    db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
    .outerjoin(models.Vote, models.Vote.post_id == models.Post.id)
    .group_by(models.Post.id)
    .all()
)
```

## 20. Alembic Migrations

Alembic manages database schema changes.

Install:

```bash
python -m pip install alembic
```

Initialize:

```bash
alembic init alembic
```

Create migration:

```bash
alembic revision --autogenerate -m "create users and posts"
```

Apply:

```bash
alembic upgrade head
```

Downgrade:

```bash
alembic downgrade -1
```

Migration rule:

- Do not rely on `Base.metadata.create_all()` in production.
- Use migrations so schema changes are versioned and repeatable.

## 21. Project Structure

```txt
app/
  main.py
  config.py
  database.py
  models.py
  schemas.py
  oauth2.py
  utils.py
  routers/
    posts.py
    users.py
    auth.py
    votes.py
alembic/
tests/
pyproject.toml
```

## 22. FastAPI Request Lifecycle

```mermaid
sequenceDiagram
  participant Client
  participant FastAPI
  participant Dependency
  participant DB
  Client->>FastAPI: HTTP request
  FastAPI->>FastAPI: Validate path/query/body
  FastAPI->>Dependency: Resolve Depends
  Dependency->>DB: Open session
  FastAPI->>DB: Query or mutate
  DB-->>FastAPI: Result
  FastAPI-->>Client: JSON response
```

