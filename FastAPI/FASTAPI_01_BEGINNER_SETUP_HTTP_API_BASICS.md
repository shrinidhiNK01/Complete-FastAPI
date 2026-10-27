# Beginner Setup, HTTP, and API Basics

## 1. What Is an API?

API means Application Programming Interface.

Simple meaning:

```text
An API lets two software systems talk to each other.
```

Example:

- Frontend app asks backend API for posts.
- Backend API returns posts as JSON.
- Mobile app sends login details to API.
- API checks user and returns token.

## 2. What Is FastAPI?

FastAPI is a Python framework for building APIs.

It is popular because:

- Fast performance
- Simple syntax
- Automatic docs
- Built-in validation
- Type hint support
- Works well with Pydantic
- Supports async
- Good for production APIs

FastAPI is usually served by ASGI servers such as Uvicorn.

## 3. Backend API Project Architecture

Typical flow:

```text
Client/Postman/Frontend
        |
HTTP request
        |
FastAPI route
        |
Pydantic validation
        |
Business logic
        |
Database through SQLAlchemy
        |
JSON response
```

## 4. Install Python

Check Python:

```bash
python --version
```

On some systems:

```bash
python3 --version
```

Use a recent Python version supported by your dependencies.

## 5. Install VS Code

Recommended extensions:

- Python
- Pylance
- Ruff or Python linting extension
- Docker
- GitHub Actions
- PostgreSQL extension if useful

## 6. Virtual Environment

A virtual environment isolates packages for one project.

Why needed:

- Avoid package conflicts
- Keep project dependencies separate
- Make deployment easier

Create venv:

```bash
python -m venv venv
```

Activate on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Activate on Windows cmd:

```cmd
venv\Scripts\activate
```

Activate on Mac/Linux:

```bash
source venv/bin/activate
```

Deactivate:

```bash
deactivate
```

## 7. Install Dependencies

Basic FastAPI:

```bash
pip install fastapi uvicorn
```

Common full project dependencies:

```bash
pip install fastapi "uvicorn[standard]" sqlalchemy psycopg[binary] alembic pydantic-settings python-jose[cryptography] passlib[bcrypt] python-multipart pytest httpx
```

Freeze dependencies:

```bash
pip freeze > requirements.txt
```

Install from requirements:

```bash
pip install -r requirements.txt
```

## 8. HTTP Basics

HTTP is the protocol used by web clients and servers.

Request contains:

- Method
- URL
- Headers
- Optional body

Response contains:

- Status code
- Headers
- Body

## 9. HTTP Methods

Common methods:

```text
GET     read data
POST    create data
PUT     replace/update full resource
PATCH   partial update
DELETE  delete data
```

Example:

```text
GET /posts
POST /posts
GET /posts/10
PUT /posts/10
DELETE /posts/10
```

## 10. Status Codes

Common status codes:

```text
200 OK
201 Created
204 No Content
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Validation Error
500 Internal Server Error
```

## 11. JSON

Most APIs send and receive JSON.

Example:

```json
{
  "title": "My first post",
  "content": "Hello FastAPI",
  "published": true
}
```

## 12. REST Basics

REST is an API design style.

Good REST paths use nouns:

```text
/posts
/users
/votes
```

Avoid action-style paths when resource style is better:

```text
/createPost
/deleteUser
```

Use HTTP methods to express action:

```text
POST /posts       create post
DELETE /posts/1   delete post 1
```

## 13. Postman Basics

Postman is used to test APIs.

You can:

- Send GET/POST/PUT/DELETE requests
- Add JSON body
- Add auth token
- Save collections
- Create environments
- Use variables
- Run test scripts

## 14. First FastAPI App

Create `main.py`:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}
```

Run:

```bash
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Docs:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc
```

## 15. What `main:app` Means

```text
main = Python file main.py
app = FastAPI object inside that file
```

`--reload` restarts server when code changes. Use it only in development.

## 16. Beginner Interview Summary

```text
FastAPI is a Python framework for building APIs. A client sends an HTTP request, FastAPI matches it to a path operation, validates input using type hints and Pydantic, runs Python logic, and returns a JSON response. It also automatically generates interactive API documentation.
```
