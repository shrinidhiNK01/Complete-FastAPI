# FastAPI Interview Q&A Cheatsheet

## 1. What Is FastAPI?

FastAPI is a Python web framework for building APIs. It uses type hints and Pydantic for validation and automatically generates OpenAPI documentation.

## 2. What Is ASGI?

ASGI is the asynchronous server interface used by frameworks like FastAPI. Uvicorn is an ASGI server.

## 3. What Is a Path Operation?

A path operation maps an HTTP method and URL path to a Python function.

## 4. Path Parameter vs Query Parameter?

Path parameter is part of the URL path, such as `/posts/1`. Query parameter comes after `?`, such as `/posts?limit=10`.

## 5. Why Path Order Matters?

FastAPI checks routes in order. Fixed routes like `/posts/latest` should come before dynamic routes like `/posts/{id}`.

## 6. What Is Pydantic?

Pydantic validates and serializes data using Python type hints.

## 7. What Is Response Model?

Response model controls and validates the shape of data returned by an endpoint.

## 8. Why Not Return Password in Response?

It leaks sensitive information. Use response models that exclude password fields.

## 9. What Is CRUD?

Create, Read, Update, Delete.

## 10. What Is SQLAlchemy?

SQLAlchemy is a Python ORM and SQL toolkit that maps Python classes to database tables.

## 11. Pydantic Model vs SQLAlchemy Model?

Pydantic model defines request/response shape. SQLAlchemy model defines database table structure.

## 12. What Is Alembic?

Alembic is a migration tool for version-controlled database schema changes.

## 13. What Is JWT?

JWT is a signed token used to represent authenticated user claims.

## 14. Is JWT Encrypted?

No. It is signed, not encrypted. Do not store secrets inside JWT payload.

## 15. What Is OAuth2PasswordBearer?

It is a FastAPI security dependency that reads bearer tokens from the Authorization header.

## 16. How Do You Protect a Route?

Add a dependency like `current_user = Depends(get_current_user)`.

## 17. What Is Password Hashing?

Password hashing stores irreversible hashes instead of plain passwords.

## 18. What Is CORS?

CORS controls whether browsers allow frontend apps from different origins to call your API.

## 19. What Is Dependency Injection in FastAPI?

It lets FastAPI provide reusable values like database sessions, current users, or settings to endpoints.

## 20. What Is `Depends`?

`Depends` declares a dependency function that FastAPI should call.

## 21. What Is `get_db`?

It is a dependency that creates a database session for a request and closes it after the request.

## 22. What Is a Foreign Key?

A foreign key links one table to another, such as posts.owner_id referencing users.id.

## 23. What Is a Join?

A join combines rows from multiple tables based on related columns.

## 24. What Is a Vote Table?

A vote table connects users and posts. A composite primary key prevents duplicate votes.

## 25. What Is `ON DELETE CASCADE`?

It automatically deletes child rows when the parent row is deleted.

## 26. What Is Environment Variable?

An external configuration value such as database password or secret key.

## 27. Why Use `.env`?

To keep local config separate from code. Real production secrets should be managed securely.

## 28. What Is Gunicorn?

Gunicorn is a production process manager/server often used with Uvicorn workers for Python web apps.

## 29. What Is NGINX Used For?

NGINX can act as a reverse proxy, handle HTTP/HTTPS, serve static files, and forward requests to FastAPI.

## 30. What Is systemd?

systemd manages Linux services and can keep the FastAPI app running after reboot or crash.

## 31. What Is Docker?

Docker packages an app and its environment into containers.

## 32. What Is Docker Compose?

Docker Compose runs multiple services, such as FastAPI API and PostgreSQL database.

## 33. What Is CI/CD?

CI automatically tests code changes. CD automatically deploys after tests pass.

## 34. What Is GitHub Actions?

GitHub Actions automates workflows such as testing, building Docker images, and deployment.

## 35. How Do You Test FastAPI?

Use pytest and FastAPI TestClient, override dependencies, and use a test database.

## 36. What Are Fixtures?

Reusable pytest setup functions for clients, users, database sessions, and tokens.

## 37. Why Separate Test Database?

To avoid damaging development or production data.

## 38. What Is SQL Injection?

An attack where user input modifies SQL query behavior. Prevent it with parameterized queries or ORM query building.

## 39. How Do You Deploy FastAPI on Ubuntu?

Install Python/Postgres, configure env vars, run Alembic migrations, serve with Gunicorn/Uvicorn, manage with systemd, proxy through NGINX, enable SSL, and configure firewall.

## 40. Final 60-Second Answer

```text
FastAPI is a Python API framework that uses type hints and Pydantic for validation and automatic OpenAPI docs. A production app usually has routers, schemas, SQLAlchemy models, database sessions, Alembic migrations, JWT auth, password hashing, protected routes, relationships, joins, and environment-based settings. PostgreSQL stores data, SQLAlchemy queries it, and Pydantic controls input/output. Testing is done with pytest and TestClient using a separate test database. Deployment can be done with Docker or on Ubuntu using Gunicorn/Uvicorn, systemd, NGINX, SSL, firewall, and CI/CD through GitHub Actions.
```
