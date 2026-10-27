# Users, Authentication, JWT, Routers, Relationships, and Votes

## 1. Users Table

Users are needed for authentication and ownership.

SQLAlchemy model:

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
```

Never store plain passwords.

## 2. User Registration Schema

```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
```

Response should not include password.

```python
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime
```

## 3. Password Hashing

Hashing converts password into irreversible stored value.

Install:

```bash
pip install passlib[bcrypt]
```

Utility:

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

## 4. Create User Endpoint

```python
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = utils.hash_password(user.password)
    new_user = models.User(email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
```

## 5. Get User by ID

```python
@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## 6. FastAPI Routers

Routers split routes into separate files.

`routers/post.py`:

```python
from fastapi import APIRouter

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.get("/")
def get_posts():
    return []
```

`main.py`:

```python
from fastapi import FastAPI
from .routers import post, user, auth, vote

app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)
```

## 7. Router Prefix and Tags

Prefix:

```python
prefix="/posts"
```

So route `@router.get("/")` becomes:

```text
GET /posts/
```

Tags organize docs:

```python
tags=["Posts"]
```

## 8. JWT Basics

JWT means JSON Web Token.

It has three parts:

```text
header.payload.signature
```

Use:

1. User logs in.
2. Server verifies email/password.
3. Server creates signed token.
4. Client sends token with future requests.
5. Server verifies token and identifies user.

JWT is signed, not encrypted. Do not put secrets in token payload.

## 9. OAuth2 Password Flow

FastAPI commonly uses:

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
```

Client sends token:

```text
Authorization: Bearer <token>
```

## 10. Create JWT Token

Install:

```bash
pip install python-jose[cryptography]
```

`oauth2.py`:

```python
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

SECRET_KEY = "replace-with-env-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

## 11. Token Data Schema

```python
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int | None = None
```

## 12. Login Endpoint

OAuth2 form requires `username` and `password`.

```python
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

@router.post("/login", response_model=schemas.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username
    ).first()

    if not user or not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials"
        )

    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
```

## 13. Verify Current User

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=user_id)
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    if user is None:
        raise credentials_exception
    return user
```

## 14. Protect Routes

```python
@router.post("/", status_code=201, response_model=schemas.PostOut)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post
```

## 15. Ownership Rules

Only owner can update/delete their own posts.

```python
if post.owner_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not authorized")
```

## 16. Retrieve Only Logged-in User's Posts

```python
posts = db.query(models.Post).filter(
    models.Post.owner_id == current_user.id
).all()
```

For public feed, retrieve all posts. For private dashboard, filter by current user.

## 17. SQLAlchemy Relationships

Post belongs to user:

```python
class Post(Base):
    owner_id = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    owner = relationship("User")
```

User has posts:

```python
class User(Base):
    posts = relationship("Post")
```

Relationship helps access:

```python
post.owner.email
```

## 18. Query Parameters for Search/Pagination

```python
@router.get("/")
def get_posts(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: str | None = ""
):
    posts = db.query(models.Post).filter(
        models.Post.title.contains(search)
    ).limit(limit).offset(skip).all()
    return posts
```

## 19. Vote/Like Theory

A vote means:

```text
User likes a post.
```

Rules:

- User must be logged in.
- User can vote a post once.
- User can remove vote.
- Vote table connects users and posts.

## 20. Vote SQLAlchemy Model

```python
class Vote(Base):
    __tablename__ = "votes"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True
    )
```

## 21. Vote Schema

```python
class Vote(BaseModel):
    post_id: int
    dir: int
```

`dir=1` means add vote.

`dir=0` means remove vote.

## 22. Vote Route

```python
@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(
    vote: schemas.Vote,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id,
        models.Vote.user_id == current_user.id
    )
    found_vote = vote_query.first()

    if vote.dir == 1:
        if found_vote:
            raise HTTPException(status_code=409, detail="User already voted")
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "Vote added"}

    if not found_vote:
        raise HTTPException(status_code=404, detail="Vote does not exist")

    vote_query.delete(synchronize_session=False)
    db.commit()
    return {"message": "Vote removed"}
```

## 23. Joins in SQLAlchemy

Get posts with vote count:

```python
from sqlalchemy import func

posts = db.query(
    models.Post,
    func.count(models.Vote.post_id).label("votes")
).join(
    models.Vote,
    models.Vote.post_id == models.Post.id,
    isouter=True
).group_by(models.Post.id).all()
```

## 24. Post With Votes Response

```python
class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    content: str
    published: bool
    created_at: datetime
    owner_id: int
    owner: UserOut

class PostOutWithVotes(BaseModel):
    Post: PostOut
    votes: int
```

## 25. Auth Interview Summary

```text
FastAPI authentication usually creates users with hashed passwords, verifies credentials during login, returns a signed JWT access token, and protects routes using OAuth2PasswordBearer dependencies. The current user is decoded from the token and used for authorization rules such as allowing only post owners to update or delete their posts.
```
