# 04. Auth, Testing, Deployment, Docker, And CI/CD

## 1. Password Hashing

Never store plain text passwords.

Install:

```bash
python -m pip install "passlib[bcrypt]"
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

Line by line:

- `CryptContext` manages password hashing schemes.
- `hash_password` turns plain password into a secure hash.
- `verify_password` checks login password against stored hash.

## 2. User Registration

```python
@router.post("/users", status_code=201, response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed = hash_password(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

Do not return password hashes in responses.

## 3. JWT Basics

JWT means JSON Web Token.

It contains claims and is signed by the server.

Flow:

```mermaid
sequenceDiagram
  participant User
  participant API
  User->>API: email + password
  API->>API: verify password
  API-->>User: access token
  User->>API: Authorization: Bearer token
  API->>API: verify token
  API-->>User: protected data
```

## 4. Create Token

Install:

```bash
python -m pip install "python-jose[cryptography]"
```

Code:

```python
from datetime import UTC, datetime, timedelta

from jose import jwt

SECRET_KEY = "change-this-in-env"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

Use environment variables for `SECRET_KEY`.

## 5. Login With OAuth2PasswordRequestForm

```python
from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login")
def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.email == credentials.username).first()
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=403, detail="Invalid credentials")

    token = create_access_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}
```

OAuth2 form uses `username`, even if your app treats it as email.

## 6. Current User Dependency

```python
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    user = db.get(models.User, int(user_id))
    if user is None:
        raise credentials_exception
    return user
```

Protected route:

```python
@router.get("/me")
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user
```

## 7. Protecting Owner Routes

```python
@router.delete("/posts/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    post = db.get(models.Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(post)
    db.commit()
```

Authentication answers "who are you?" Authorization answers "are you allowed?"

## 8. CORS

CORS controls whether browsers allow frontend JavaScript from one origin to call an API at another origin.

```python
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
    "https://example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Do not use `allow_origins=["*"]` with credentials in production.

## 9. FastAPI TestClient

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_read_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
```

## 10. Testing Database Pattern

Use a separate test database.

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "postgresql+psycopg://postgres:password@localhost:5432/fastapi_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(session):
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

For production-like tests, prefer Alembic migrations over `create_all`.

## 11. Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY app ./app

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
```

Line by line:

- `FROM` chooses Python base image.
- `WORKDIR` sets working folder.
- Environment variables improve container behavior.
- `COPY pyproject.toml` copies dependency metadata first.
- `RUN pip install` installs app dependencies.
- `COPY app` copies source code.
- `CMD` starts the API.

## 12. Docker Compose With Postgres

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+psycopg://postgres:postgres@db:5432/app
      SECRET_KEY: dev-secret
    depends_on:
      - db

  db:
    image: postgres:17
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run:

```bash
docker compose up --build
```

## 13. Ubuntu VM Deployment

High-level steps:

1. Create Ubuntu VM.
2. SSH into server.
3. Update packages.
4. Install Python.
5. Install Postgres.
6. Create Linux app user.
7. Clone repository.
8. Create virtual environment.
9. Install dependencies.
10. Set environment variables.
11. Run Alembic migrations.
12. Configure Gunicorn/Uvicorn.
13. Create systemd service.
14. Configure NGINX reverse proxy.
15. Configure domain DNS.
16. Enable HTTPS with Certbot.
17. Configure firewall.

## 14. Gunicorn With Uvicorn Workers

```bash
gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8000 \
  --workers 4
```

Meaning:

- `gunicorn` manages worker processes.
- `app.main:app` points to FastAPI app.
- `UvicornWorker` runs ASGI app.
- `127.0.0.1:8000` exposes only locally.
- NGINX handles public traffic.

## 15. systemd Service

```ini
[Unit]
Description=FastAPI application
After=network.target

[Service]
User=fastapi
Group=fastapi
WorkingDirectory=/home/fastapi/app
EnvironmentFile=/home/fastapi/app/.env
ExecStart=/home/fastapi/app/.venv/bin/gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Commands:

```bash
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi
sudo systemctl status fastapi
```

## 16. NGINX Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

NGINX receives internet traffic and forwards it to the local FastAPI server.

## 17. GitHub Actions CI

`.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_DB: app_test
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install ".[dev]"

      - name: Lint
        run: ruff check .

      - name: Type check
        run: mypy app

      - name: Test
        env:
          DATABASE_URL: postgresql+psycopg://postgres:postgres@localhost:5432/app_test
          SECRET_KEY: test-secret
        run: pytest
```

## 18. Deployment Checklist

Before production:

- Environment variables set.
- Secret key strong and private.
- Database migrations applied.
- HTTPS enabled.
- CORS restricted.
- Logs available.
- Tests passing.
- CI pipeline green.
- Backups configured.
- Monitoring configured.
- Debug mode off.

