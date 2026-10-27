# 02. Tooling, Packaging, And Code Quality

## 1. Installing Python

Install Python from:

- Python.org.
- pyenv on macOS/Linux.
- uv, rye, or other modern environment tools if your team uses them.
- Microsoft Store is convenient on Windows, but python.org installers are often clearer for development.

Check:

```bash
python --version
python -m pip --version
```

On some systems, use:

```bash
python3 --version
python3 -m pip --version
```

## 2. VS Code Setup

Install:

- Python extension.
- Pylance.
- Ruff extension.
- Docker extension if deploying containers.
- Jupyter extension for data work.

Use the project virtual environment as the interpreter.

## 3. Virtual Environments

A virtual environment isolates project dependencies.

Create:

```bash
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activate on macOS/Linux:

```bash
source .venv/bin/activate
```

Install packages:

```bash
python -m pip install fastapi uvicorn sqlalchemy psycopg pydantic
```

## 4. pip Basics

Install:

```bash
python -m pip install requests
```

Freeze:

```bash
python -m pip freeze > requirements.txt
```

Install from file:

```bash
python -m pip install -r requirements.txt
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

## 5. Modern Project Layout

Recommended layout:

```txt
my_project/
  pyproject.toml
  README.md
  src/
    my_project/
      __init__.py
      app.py
  tests/
    test_app.py
```

Why `src` layout helps:

- Prevents accidentally importing local files instead of installed package.
- Makes packaging behavior closer to production.

## 6. pyproject.toml

`pyproject.toml` is the central configuration file for modern Python projects.

Example:

```toml
[project]
name = "fastapi-social-api"
version = "0.1.0"
description = "A FastAPI backend with PostgreSQL"
requires-python = ">=3.12"
dependencies = [
  "fastapi[standard]",
  "sqlalchemy>=2.0",
  "psycopg[binary]>=3.2",
  "alembic",
  "pydantic-settings",
  "passlib[bcrypt]",
  "python-jose[cryptography]",
]

[project.optional-dependencies]
dev = [
  "pytest",
  "httpx",
  "ruff",
  "black",
  "mypy",
]

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.black]
line-length = 88

[tool.mypy]
python_version = "3.12"
strict = true
```

Line by line:

- `[project]` defines package metadata.
- `requires-python` sets supported Python versions.
- `dependencies` lists runtime dependencies.
- `[project.optional-dependencies]` defines extras like dev tools.
- `[tool.ruff]`, `[tool.black]`, and `[tool.mypy]` configure tools.

## 7. Ruff

Ruff is a fast Python linter and formatter.

Run lint:

```bash
ruff check .
```

Auto-fix:

```bash
ruff check . --fix
```

Format:

```bash
ruff format .
```

Good starting config:

```toml
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM"]
```

Meaning:

- `E`, `F`: pycodestyle/pyflakes style checks.
- `I`: import sorting.
- `B`: bugbear checks.
- `UP`: modern Python upgrade suggestions.
- `SIM`: simplification suggestions.

## 8. Black

Black is an opinionated formatter.

Run:

```bash
black .
```

Black reduces formatting debates. Ruff can also format, so many teams now use Ruff alone or Ruff plus Black depending on preference.

## 9. mypy

mypy checks type hints.

Example:

```python
def add(a: int, b: int) -> int:
    return a + b

add("1", "2")
```

mypy flags the wrong argument types.

Run:

```bash
mypy src
```

Type hints are most valuable at module boundaries:

- API schemas.
- Database layer.
- Service functions.
- ML pipeline inputs/outputs.

## 10. pytest

Test file:

```python
def add(a: int, b: int) -> int:
    return a + b

def test_add() -> None:
    assert add(2, 3) == 5
```

Run:

```bash
pytest
pytest -v
pytest -s
```

`-v` is verbose. `-s` shows print output.

## 11. Parametrize

```python
import pytest

@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (1, 2, 3),
        (0, 0, 0),
        (-1, 1, 0),
    ],
)
def test_add(a: int, b: int, expected: int) -> None:
    assert a + b == expected
```

Parametrize runs one test with multiple inputs.

## 12. Fixtures

```python
import pytest

@pytest.fixture
def sample_user() -> dict[str, str]:
    return {"email": "user@example.com", "password": "secret"}

def test_user_email(sample_user: dict[str, str]) -> None:
    assert sample_user["email"] == "user@example.com"
```

Fixtures prepare reusable test data or resources.

## 13. Environment Variables

Do not hardcode secrets.

Example:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 30

settings = Settings()
```

`.env`:

```txt
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/app
SECRET_KEY=change-me
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 14. Pre-commit Quality Workflow

Before pushing:

```bash
ruff check . --fix
ruff format .
mypy src
pytest
```

CI should run the same commands.

## 15. Dependency Strategy

For apps:

- Pin exact versions in a lockfile if using a lock-capable tool.
- Keep `pyproject.toml` readable.
- Update dependencies regularly.
- Run tests after updates.

For libraries:

- Avoid overly strict dependency pins.
- Define compatible ranges.

## 16. Logging

Use logging instead of print in applications.

```python
import logging

logger = logging.getLogger(__name__)

def create_user(email: str) -> None:
    logger.info("Creating user", extra={"email": email})
```

Never log passwords, tokens, or secrets.

