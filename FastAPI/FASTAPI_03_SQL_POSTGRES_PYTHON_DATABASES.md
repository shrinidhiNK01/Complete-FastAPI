# SQL, PostgreSQL, and Python Database Basics

## 1. Why Use a Database?

In-memory data is temporary. A database stores data permanently.

Databases give:

- Persistence
- Querying
- Indexing
- Relationships
- Transactions
- Security
- Backups
- Multi-user access

## 2. What Is PostgreSQL?

PostgreSQL is a powerful open-source relational database.

It stores data in tables.

Example table:

```text
posts
id | title | content | published | created_at
```

## 3. Database, Table, Row, Column

Database:

```text
Collection of related tables.
```

Table:

```text
Structured data with rows and columns.
```

Row:

```text
One record.
```

Column:

```text
One field.
```

## 4. Install PostgreSQL

Windows:

- Install PostgreSQL installer
- Remember password for `postgres` user
- pgAdmin is often included

Mac:

- Use official installer or Homebrew

```bash
brew install postgresql
```

Linux/Ubuntu:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

## 5. pgAdmin

pgAdmin is a GUI for PostgreSQL.

You can:

- Create database
- Create tables
- Run SQL queries
- View rows
- Manage users
- Inspect schemas

## 6. SQL Basics

SQL means Structured Query Language.

It is used to:

- Create tables
- Insert data
- Read data
- Update data
- Delete data
- Join tables

## 7. Create Table

```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    published BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

## 8. Insert Data

```sql
INSERT INTO posts (title, content, published)
VALUES ('First Post', 'Hello API', true);
```

## 9. Select Data

```sql
SELECT * FROM posts;
```

Specific columns:

```sql
SELECT title, content FROM posts;
```

## 10. WHERE Filter

```sql
SELECT * FROM posts
WHERE id = 1;
```

## 11. SQL Operators

```sql
=
!=
>
<
>=
<=
AND
OR
NOT
```

Example:

```sql
SELECT * FROM posts
WHERE published = true AND id > 10;
```

## 12. IN

```sql
SELECT * FROM posts
WHERE id IN (1, 2, 3);
```

## 13. LIKE and ILIKE

Pattern matching:

```sql
SELECT * FROM posts
WHERE title LIKE '%python%';
```

PostgreSQL case-insensitive:

```sql
SELECT * FROM posts
WHERE title ILIKE '%python%';
```

## 14. ORDER BY

```sql
SELECT * FROM posts
ORDER BY created_at DESC;
```

## 15. LIMIT and OFFSET

```sql
SELECT * FROM posts
LIMIT 10 OFFSET 20;
```

Used for pagination.

## 16. Update Data

```sql
UPDATE posts
SET title = 'Updated title'
WHERE id = 1
RETURNING *;
```

## 17. Delete Data

```sql
DELETE FROM posts
WHERE id = 1
RETURNING *;
```

## 18. Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

## 19. Foreign Keys

Foreign key connects tables.

```sql
ALTER TABLE posts
ADD COLUMN owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE;
```

Meaning:

```text
Each post belongs to one user.
```

## 20. Votes Table

```sql
CREATE TABLE votes (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, post_id)
);
```

Composite primary key prevents one user from liking same post multiple times.

## 21. Joins

Join combines rows from multiple tables.

```sql
SELECT posts.*, users.email
FROM posts
JOIN users ON posts.owner_id = users.id;
```

Vote count:

```sql
SELECT posts.*, COUNT(votes.post_id) AS votes
FROM posts
LEFT JOIN votes ON posts.id = votes.post_id
GROUP BY posts.id;
```

`LEFT JOIN` keeps posts even if they have zero votes.

## 22. Python Database Connection

Modern PostgreSQL driver option:

```bash
pip install psycopg[binary]
```

Basic connection:

```python
import psycopg

conn = psycopg.connect(
    host="localhost",
    dbname="fastapi",
    user="postgres",
    password="password"
)

cur = conn.cursor()
cur.execute("SELECT * FROM posts")
rows = cur.fetchall()
print(rows)
cur.close()
conn.close()
```

## 23. Parameterized Queries

Never build SQL by string concatenation with user input.

Bad:

```python
cur.execute(f"SELECT * FROM posts WHERE id = {id}")
```

Good:

```python
cur.execute("SELECT * FROM posts WHERE id = %s", (id,))
```

This helps prevent SQL injection.

## 24. Raw SQL CRUD

Create:

```python
cur.execute(
    "INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *",
    (post.title, post.content, post.published)
)
new_post = cur.fetchone()
conn.commit()
```

Read:

```python
cur.execute("SELECT * FROM posts WHERE id = %s", (id,))
post = cur.fetchone()
```

Update:

```python
cur.execute(
    "UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *",
    (post.title, post.content, post.published, id)
)
updated = cur.fetchone()
conn.commit()
```

Delete:

```python
cur.execute("DELETE FROM posts WHERE id=%s RETURNING *", (id,))
deleted = cur.fetchone()
conn.commit()
```

## 25. Why Use ORM After Learning SQL?

Raw SQL is powerful, but ORM helps:

- Map tables to Python classes
- Reduce repeated SQL
- Manage relationships
- Build queries programmatically
- Integrate with migrations

Still learn SQL. ORM does not replace SQL understanding.

## 26. Database Interview Summary

```text
PostgreSQL stores API data permanently in relational tables. SQL is used to create, query, update, delete, filter, order, paginate, and join data. Foreign keys model relationships, and parameterized queries prevent SQL injection. In production FastAPI apps, SQLAlchemy is commonly used as an ORM over PostgreSQL.
```
