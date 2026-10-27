# Deployment, Docker, Ubuntu, NGINX, SSL, and CI/CD

## 1. Development vs Production

Development:

- `uvicorn --reload`
- Local database
- Debug logs
- Local `.env`

Production:

- No reload
- Real database
- HTTPS
- Firewall
- Secrets management
- Process manager
- Monitoring/logging
- CI/CD

## 2. Pre-Deployment Checklist

- Tests pass
- `.env` not committed
- Production database ready
- Alembic migrations ready
- CORS configured
- App imports correctly
- Requirements file complete
- Secrets configured
- Error logs available
- HTTPS planned

## 3. Heroku-Style Deployment

Heroku-style deployment usually needs:

- Git repo
- `requirements.txt`
- `Procfile`
- Environment variables
- PostgreSQL add-on/database
- Run Alembic migrations

`Procfile`:

```text
web: gunicorn app.main:app -k uvicorn.workers.UvicornWorker
```

Note: cloud platforms change over time. Always check the platform's current docs for exact commands, pricing, add-ons, and Python runtime support.

## 4. Ubuntu VM Deployment Overview

Flow:

```text
Create VM
Install system packages
Install Python
Install PostgreSQL
Create Linux user
Clone repo
Create virtual environment
Install dependencies
Configure environment variables
Run Alembic migrations
Run app with Gunicorn/Uvicorn
Create systemd service
Put NGINX reverse proxy in front
Add domain
Enable SSL
Configure firewall
Deploy future changes
```

## 5. Update Ubuntu Packages

```bash
sudo apt update
sudo apt upgrade -y
```

## 6. Install Python and Tools

```bash
sudo apt install -y python3 python3-venv python3-pip git
```

## 7. Install PostgreSQL

```bash
sudo apt install -y postgresql postgresql-contrib
```

Switch user:

```bash
sudo -u postgres psql
```

Create database/user:

```sql
CREATE DATABASE fastapi_prod;
CREATE USER fastapi_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE fastapi_prod TO fastapi_user;
```

## 8. PostgreSQL Config

For local app on same server, default local access is often enough.

For remote DB access, configure carefully:

- `postgresql.conf`
- `pg_hba.conf`
- firewall
- strong passwords
- SSL if needed

Do not expose PostgreSQL publicly unless you know what you are doing.

## 9. Create App User

```bash
sudo adduser fastapi
sudo usermod -aG sudo fastapi
```

Use app user instead of root.

## 10. Clone and Setup App

```bash
git clone <repo-url>
cd <repo>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 11. Production Environment Variables

Create env file:

```bash
sudo nano /etc/fastapi.env
```

Example:

```text
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_PASSWORD=strong_password
DATABASE_NAME=fastapi_prod
DATABASE_USERNAME=fastapi_user
SECRET_KEY=long_random_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Restrict permissions:

```bash
sudo chmod 600 /etc/fastapi.env
```

## 12. Alembic Migrations on Production

```bash
source venv/bin/activate
alembic upgrade head
```

## 13. Gunicorn + Uvicorn Worker

Install:

```bash
pip install gunicorn uvicorn
```

Run:

```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 2 -b 127.0.0.1:8000
```

Important: Check current Uvicorn/Gunicorn docs because worker packaging details may change over time.

## 14. systemd Service

`/etc/systemd/system/fastapi.service`:

```ini
[Unit]
Description=FastAPI application
After=network.target

[Service]
User=fastapi
Group=fastapi
WorkingDirectory=/home/fastapi/app
EnvironmentFile=/etc/fastapi.env
ExecStart=/home/fastapi/app/venv/bin/gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 2 -b 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi
sudo systemctl status fastapi
```

Logs:

```bash
sudo journalctl -u fastapi -f
```

## 15. NGINX Reverse Proxy

Install:

```bash
sudo apt install -y nginx
```

Config:

```nginx
server {
    listen 80;
    server_name example.com www.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 16. Domain Name

Set DNS A record:

```text
example.com -> server_public_ip
```

DNS propagation may take time.

## 17. SSL/HTTPS

Install Certbot:

```bash
sudo apt install -y certbot python3-certbot-nginx
```

Create certificate:

```bash
sudo certbot --nginx -d example.com -d www.example.com
```

Renewal test:

```bash
sudo certbot renew --dry-run
```

## 18. Firewall

UFW:

```bash
sudo ufw allow OpenSSH
sudo ufw allow "Nginx Full"
sudo ufw enable
sudo ufw status
```

## 19. Deploy Code Changes

```bash
git pull
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart fastapi
```

## 20. Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 21. Docker Compose with Postgres

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: fastapi
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run:

```bash
docker compose up --build
```

## 22. Bind Mounts

Bind mount maps local folder into container.

Useful in development:

```yaml
volumes:
  - .:/app
```

Do not blindly use development bind mounts in production.

## 23. Docker Hub

Build:

```bash
docker build -t username/fastapi-app:latest .
```

Push:

```bash
docker push username/fastapi-app:latest
```

## 24. GitHub Actions CI/CD

`.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: password
          POSTGRES_DB: fastapi_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    env:
      DATABASE_HOSTNAME: localhost
      DATABASE_PORT: 5432
      DATABASE_PASSWORD: password
      DATABASE_NAME: fastapi_test
      DATABASE_USERNAME: postgres
      SECRET_KEY: test_secret
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 30

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run migrations
        run: alembic upgrade head

      - name: Run tests
        run: pytest -v
```

## 25. CI/CD Concepts

CI means Continuous Integration:

```text
Automatically test every push/pull request.
```

CD means Continuous Deployment:

```text
Automatically deploy after tests pass.
```

Use GitHub Secrets for sensitive values.

## 26. Deployment Interview Summary

```text
For production, I configure environment variables, run Alembic migrations, serve FastAPI with Gunicorn/Uvicorn, manage the process with systemd, put NGINX in front as a reverse proxy, enable HTTPS with Certbot, protect the server with a firewall, and use CI/CD to test and deploy changes. Docker can package the API and PostgreSQL for consistent development and deployment.
```
