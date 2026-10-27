# Testing FastAPI with Pytest and TestClient

## 1. Why Testing Matters

Testing proves your API works.

It helps catch:

- Broken routes
- Wrong status codes
- Auth bugs
- Database bugs
- Validation bugs
- Regression after changes
- CI/CD failures before production

## 2. Install Test Dependencies

```bash
pip install pytest httpx
```

FastAPI's `TestClient` uses HTTPX/Starlette testing tools.

## 3. First Pytest Test

`test_basic.py`:

```python
def add(a: int, b: int) -> int:
    return a + b

def test_add():
    assert add(2, 3) == 5
```

Run:

```bash
pytest
```

Verbose:

```bash
pytest -v
```

Show prints:

```bash
pytest -s
```

## 4. Testing Exceptions

```python
import pytest

def divide(a, b):
    if b == 0:
        raise ValueError("division by zero")
    return a / b

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(10, 0)
```

## 5. Parametrize

```python
import pytest

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (5, 5, 10),
    (-1, 1, 0),
])
def test_add(a, b, expected):
    assert a + b == expected
```

## 6. Fixtures

Fixture provides reusable setup.

```python
import pytest

@pytest.fixture
def sample_user():
    return {"email": "test@example.com", "password": "password"}

def test_user_email(sample_user):
    assert sample_user["email"] == "test@example.com"
```

## 7. Fixture Scope

Common scopes:

- function: runs for each test
- module: once per file
- session: once per test session

```python
@pytest.fixture(scope="session")
def app_settings():
    return {"env": "test"}
```

## 8. FastAPI TestClient

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```

## 9. Testing Create User

```python
def test_create_user(client):
    response = client.post("/users/", json={
        "email": "test@example.com",
        "password": "password123"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data
```

## 10. Test Database

Never run tests against production database.

Use a separate test database:

```text
fastapi_test
```

Testing strategy:

- Create tables before tests
- Drop tables after tests
- Override app database dependency
- Use test database session

## 11. Dependency Override

FastAPI lets tests override dependencies.

```python
app.dependency_overrides[get_db] = override_get_db
```

This is how tests use test DB instead of production DB.

## 12. conftest.py

`conftest.py` stores shared fixtures.

Example:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://postgres:password@localhost:5432/fastapi_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
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
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

If your project uses Alembic, you can run migrations in tests instead of `create_all`, especially for closer production realism.

## 13. Test User Fixture

```python
@pytest.fixture
def test_user(client):
    user_data = {"email": "user@example.com", "password": "password123"}
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    user = response.json()
    user["password"] = user_data["password"]
    return user
```

## 14. Test Login and Token

```python
def test_login_user(client, test_user):
    response = client.post("/login", data={
        "username": test_user["email"],
        "password": test_user["password"]
    })
    assert response.status_code == 200
    token = response.json()
    assert token["token_type"] == "bearer"
    assert token["access_token"]
```

## 15. Authorized Client Fixture

```python
@pytest.fixture
def token(client, test_user):
    response = client.post("/login", data={
        "username": test_user["email"],
        "password": test_user["password"]
    })
    return response.json()["access_token"]

@pytest.fixture
def authorized_client(client, token):
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
```

## 16. Test Create Post

```python
def test_create_post(authorized_client):
    response = authorized_client.post("/posts/", json={
        "title": "Test post",
        "content": "Test content",
        "published": True
    })
    assert response.status_code == 201
    assert response.json()["title"] == "Test post"
```

## 17. Unauthorized Test

```python
def test_unauthorized_create_post(client):
    response = client.post("/posts/", json={
        "title": "No auth",
        "content": "No token"
    })
    assert response.status_code == 401
```

## 18. Posts Fixture

```python
@pytest.fixture
def test_posts(session, test_user):
    posts = [
        {"title": "Post 1", "content": "Content 1", "owner_id": test_user["id"]},
        {"title": "Post 2", "content": "Content 2", "owner_id": test_user["id"]},
    ]
    created = [models.Post(**post) for post in posts]
    session.add_all(created)
    session.commit()
    return created
```

## 19. Test Get All Posts

```python
def test_get_all_posts(authorized_client, test_posts):
    response = authorized_client.get("/posts/")
    assert response.status_code == 200
    assert len(response.json()) >= 2
```

## 20. Test Delete Post

```python
def test_delete_post(authorized_client, test_posts):
    response = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 204
```

## 21. Test Vote

```python
def test_vote_on_post(authorized_client, test_posts):
    response = authorized_client.post("/vote/", json={
        "post_id": test_posts[0].id,
        "dir": 1
    })
    assert response.status_code == 201
```

## 22. Trailing Slashes

FastAPI may redirect `/posts` to `/posts/` depending on route definition.

In tests, match your actual routes.

Example:

```python
client.get("/posts/")
```

## 23. Useful Pytest Flags

```bash
pytest -v
pytest -s
pytest -x
pytest --maxfail=1
pytest tests/test_posts.py
pytest -k "login"
```

## 24. Testing Interview Summary

```text
For FastAPI testing, I use pytest and TestClient. I create a separate test database, override the get_db dependency, use fixtures for users, tokens, authorized clients, and test posts, then test success cases, unauthorized cases, validation errors, ownership rules, and votes. These tests run in CI before deployment.
```
