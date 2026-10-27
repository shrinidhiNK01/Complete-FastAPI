# SQLAlchemy, Pydantic Schemas, and Alembic Migrations

## 1. What Is an ORM?

ORM means Object Relational Mapper.

It maps:

```text
Python class <-> database table
Python object <-> database row
```

SQLAlchemy is the most common ORM in Python.

## 2. Install Dependencies

```bash
pip install sqlalchemy psycopg[binary] alembic
```

## 3. Database URL

PostgreSQL URL:

```text
postgresql+psycopg://username:password@localhost:5432/database_name
```

Example:

```python
DATABASE_URL = "postgresql+psycopg://postgres:password@localhost:5432/fastapi"
```

## 4. SQLAlchemy Setup

`database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "postgresql+psycopg://postgres:password@localhost:5432/fastapi"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 5. SQLAlchemy Model

`models.py`:

```python
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    created_at = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User")
```

## 6. Create Tables Manually vs Migrations

Learning/demo:

```python
Base.metadata.create_all(bind=engine)
```

Production:

Use Alembic migrations.

After Alembic, do not rely on `create_all` for schema changes.

## 7. Dependency Injection for DB Session

FastAPI dependencies:

```python
from fastapi import Depends
from sqlalchemy.orm import Session

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    return db.query(Post).all()
```

## 8. Basic SQLAlchemy CRUD

Get all:

```python
posts = db.query(models.Post).all()
```

Create:

```python
new_post = models.Post(**post.model_dump(), owner_id=current_user.id)
db.add(new_post)
db.commit()
db.refresh(new_post)
```

Get by id:

```python
post = db.query(models.Post).filter(models.Post.id == id).first()
```

Delete:

```python
query = db.query(models.Post).filter(models.Post.id == id)
post = query.first()
query.delete(synchronize_session=False)
db.commit()
```

Update:

```python
query = db.query(models.Post).filter(models.Post.id == id)
query.update(post.model_dump(), synchronize_session=False)
db.commit()
```

## 9. Pydantic vs ORM Models

SQLAlchemy model:

```text
Defines database table.
```

Pydantic model/schema:

```text
Defines request/response data shape.
```

Do not use one model for everything.

## 10. Pydantic Schemas

`schemas.py`:

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    pass

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime

class PostOut(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut
```

## 11. Response Models

```python
@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    return post
```

Response model prevents leaking fields such as passwords.

## 12. Alembic

Alembic is a database migration tool.

Migration means:

```text
Version-controlled database schema change.
```

Examples:

- Create users table
- Add owner_id column
- Create votes table
- Roll back bad schema change

## 13. Alembic Setup

Install:

```bash
pip install alembic
```

Initialize:

```bash
alembic init alembic
```

Files:

```text
alembic.ini
alembic/env.py
alembic/versions/
```

## 14. Configure Alembic

In `alembic/env.py`, import models metadata:

```python
from app.database import Base
from app import models

target_metadata = Base.metadata
```

Set database URL from settings instead of hardcoding when possible.

## 15. Create Migration

Autogenerate:

```bash
alembic revision --autogenerate -m "create posts table"
```

Apply:

```bash
alembic upgrade head
```

Rollback one migration:

```bash
alembic downgrade -1
```

## 16. Manual Migration Example

```python
def upgrade() -> None:
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id")
    )

def downgrade() -> None:
    op.drop_table("posts")
```

## 17. Alembic Best Practices

- Review autogenerated migrations before running.
- Test migrations on test DB.
- Keep migrations in Git.
- Run migrations during deployment.
- Avoid editing old migrations after team/production use.
- Do not use `create_all` as production migration strategy.

## 18. SQLAlchemy/Alembic Interview Summary

```text
SQLAlchemy maps Python classes to database tables and lets FastAPI query PostgreSQL using sessions. Pydantic schemas validate request/response data, while SQLAlchemy models define database structure. Alembic manages schema changes through version-controlled migrations, which is safer than relying on create_all in production.
```
