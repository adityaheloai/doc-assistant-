# PostgreSQL Getting Started Guide

## What is PostgreSQL?

PostgreSQL is an open-source relational database system.

## Install Node.js Client

```bash
npm install pg
```

## Connect from Python

```bash
pip install psycopg2-binary
```

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="mydb",
    user="myuser",
    password="mypassword"
)
```

## Create Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);
```

## Insert Data

```sql
INSERT INTO users(name,email)
VALUES('John','john@example.com');
```

## Query Data

```sql
SELECT * FROM users;
```

## Update Data

```sql
UPDATE users
SET name='Jane'
WHERE id=1;
```

## Delete Data

```sql
DELETE FROM users
WHERE id=1;
```

## UUID Example

```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL
);
```

## Best Practice

Always use connection pooling in production.