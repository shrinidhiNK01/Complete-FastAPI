# Project Structure, Environment Variables, CORS, and Postman

## 1. Why Clean Project Structure Matters

Small demos can keep everything in `main.py`.

Real projects should be split by responsibility.

Benefits:

- Easier to understand
- Easier to test
- Easier to maintain
- Easier for teams
- Avoids huge `main.py`

## 2. Recommended Project Structure

```text
app/
  __init__.py
  main.py
  config.py
  database.py
  models.py
  schemas.py
  oauth2.py
  utils.py
  routers/
    __init__.py
    auth.py
    post.py
    user.py
    vote.py
alembic/
alembic.ini
requirements.txt
.env
tests/
```

## 3. File Responsibilities

`main.py`:

```text
Create FastAPI app, add middleware, include routers.
```

`database.py`:

```text
Database engine, session, Base, get_db dependency.
```

`models.py`:

```text
SQLAlchemy table models.
```

`schemas.py`:

```text
Pydantic request/response schemas.
```

`oauth2.py`:

```text
JWT creation and current-user dependency.
```

`utils.py`:

```text
Reusable helpers such as password hashing.
```

`routers/`:

```text
Separate endpoint groups.
```

## 4. Environment Variables

Environment variables store config outside code.

Examples:

- Database URL
- Secret key
- Token expiry
- Environment name
- Allowed origins

Never hardcode production secrets.

## 5. `.env` Example

```text
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_PASSWORD=password
DATABASE_NAME=fastapi
DATABASE_USERNAME=postgres
SECRET_KEY=replace_me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Do not commit real `.env` secrets to Git.

## 6. Pydantic Settings

Install:

```bash
pip install pydantic-settings
```

`config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_hostname: str
    database_port: int
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

## 7. Build Database URL from Settings

```python
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg://{settings.database_username}:"
    f"{settings.database_password}@{settings.database_hostname}:"
    f"{settings.database_port}/{settings.database_name}"
)
```

## 8. CORS

CORS means Cross-Origin Resource Sharing.

Browser blocks frontend calls to different origins unless backend allows it.

Example:

```text
Frontend: http://localhost:3000
Backend:  http://localhost:8000
```

Different port means different origin.

## 9. Add CORS Middleware

```python
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",
    "https://yourdomain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

In production, avoid allowing every origin unless necessary.

## 10. Postman Advanced Features

Use Postman for:

- Collections
- Environments
- Variables
- Auth token storage
- Pre-request scripts
- Tests
- Sharing API examples

Example environment variables:

```text
base_url=http://127.0.0.1:8000
token=<jwt token>
```

Use:

```text
{{base_url}}/posts
```

Authorization:

```text
Bearer {{token}}
```

## 11. Git Basics

Initialize:

```bash
git init
```

Check status:

```bash
git status
```

Add:

```bash
git add .
```

Commit:

```bash
git commit -m "initial fastapi app"
```

Remote:

```bash
git remote add origin <repo-url>
git push -u origin main
```

## 12. `.gitignore`

```text
venv/
__pycache__/
.env
.pytest_cache/
.coverage
htmlcov/
*.pyc
```

## 13. Requirements File

```bash
pip freeze > requirements.txt
```

Common production requirements:

```text
fastapi
uvicorn[standard]
gunicorn
sqlalchemy
psycopg[binary]
alembic
pydantic-settings
python-jose[cryptography]
passlib[bcrypt]
python-multipart
pytest
httpx
```

## 14. Project Structure Interview Summary

```text
In a real FastAPI project, I split the code into routers, schemas, models, database setup, auth utilities, config, and tests. I use environment variables for secrets and database settings, CORS middleware for frontend access, Git for version control, and Postman collections for manual API testing.
```
