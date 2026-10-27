# FastAPI Core, Path Operations, Pydantic, and CRUD

## 1. Path Operation

A path operation is one API endpoint.

```python
@app.get("/posts")
def get_posts():
    return {"data": "posts"}
```

Parts:

- `@app.get`: HTTP method decorator
- `"/posts"`: path
- `get_posts`: function
- returned dictionary becomes JSON

## 2. Path Parameters

Path parameters are values inside URL path.

```python
@app.get("/posts/{id}")
def get_post(id: int):
    return {"post_id": id}
```

FastAPI converts `id` to integer because of type hint.

If user sends `/posts/abc`, FastAPI returns validation error.

## 3. Path Order Matters

FastAPI checks routes in order.

Bad:

```python
@app.get("/posts/{id}")
def get_post(id: int): ...

@app.get("/posts/latest")
def latest_post(): ...
```

`/posts/latest` may be treated as `id`.

Good:

```python
@app.get("/posts/latest")
def latest_post(): ...

@app.get("/posts/{id}")
def get_post(id: int): ...
```

Put fixed paths before dynamic paths.

## 4. Query Parameters

Query parameters come after `?`.

```text
/posts?limit=10&skip=20&search=python
```

FastAPI:

```python
@app.get("/posts")
def get_posts(limit: int = 10, skip: int = 0, search: str | None = None):
    return {"limit": limit, "skip": skip, "search": search}
```

## 5. Request Body

For POST/PUT/PATCH, data is often sent in JSON body.

Pydantic model:

```python
from pydantic import BaseModel

class PostCreate(BaseModel):
    title: str
    content: str
    published: bool = True
```

Endpoint:

```python
@app.post("/posts")
def create_post(post: PostCreate):
    return post
```

## 6. Pydantic Validation

Pydantic validates incoming data.

If request body:

```json
{
  "title": 123,
  "content": "hello"
}
```

FastAPI/Pydantic will validate based on schema.

Validation gives:

- Type conversion when possible
- Error messages
- API docs schema

## 7. Pydantic v2 Notes

Modern Pydantic uses:

```python
from pydantic import BaseModel, ConfigDict

class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
```

Older tutorials may use:

```python
class Config:
    orm_mode = True
```

In Pydantic v2, `from_attributes=True` replaces the old ORM mode pattern.

## 8. Response Model

Response model controls output shape.

```python
@app.get("/posts/{id}", response_model=PostOut)
def get_post(id: int):
    return post
```

Benefits:

- Removes unwanted fields
- Documents response
- Validates output
- Prevents leaking sensitive data

## 9. Status Codes

```python
from fastapi import status

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate):
    return post
```

For delete:

```python
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    return None
```

## 10. HTTPException

Raise errors properly:

```python
from fastapi import HTTPException, status

if post is None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Post with id {id} was not found"
    )
```

## 11. In-Memory CRUD

This is useful for learning before database.

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

my_posts = [
    {"title": "Post 1", "content": "Content 1", "id": 1},
    {"title": "Post 2", "content": "Content 2", "id": 2},
]

def find_post(id: int):
    for post in my_posts:
        if post["id"] == id:
            return post

def find_index_post(id: int):
    for index, post in enumerate(my_posts):
        if post["id"] == id:
            return index

@app.get("/posts")
def get_posts():
    return {"data": my_posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    new_post = post.model_dump()
    new_post["id"] = my_posts[-1]["id"] + 1
    my_posts.append(new_post)
    return {"data": new_post}

@app.get("/posts/{id}")
def get_post(id: int):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"data": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_index_post(id)
    if index is None:
        raise HTTPException(status_code=404, detail="Post not found")
    my_posts.pop(index)
    return None

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_index_post(id)
    if index is None:
        raise HTTPException(status_code=404, detail="Post not found")
    updated = post.model_dump()
    updated["id"] = id
    my_posts[index] = updated
    return {"data": updated}
```

## 12. Why In-Memory Array Is Not Production

Problems:

- Data disappears when server restarts
- Not shared across multiple workers
- No transactions
- No indexing
- No relationships
- No persistence

Use database for real apps.

## 13. Automatic Documentation

FastAPI generates docs from:

- Routes
- Type hints
- Pydantic models
- Status codes
- Response models

Swagger UI:

```text
/docs
```

ReDoc:

```text
/redoc
```

OpenAPI JSON:

```text
/openapi.json
```

## 14. Python Packages

A package is a folder with Python modules.

Common project structure:

```text
app/
  __init__.py
  main.py
  schemas.py
  models.py
  database.py
  routers/
    __init__.py
    post.py
    user.py
```

`__init__.py` tells Python this folder is a package.

## 15. Core Interview Summary

```text
FastAPI path operations map HTTP methods and paths to Python functions. Path and query parameters are parsed from the URL, request bodies are validated by Pydantic models, and response models control what is returned. HTTPException is used for API errors, and FastAPI automatically creates OpenAPI docs from the code.
```
