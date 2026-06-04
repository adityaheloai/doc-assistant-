# FastAPI Introduction

## What is FastAPI?

FastAPI is a modern Python framework for building APIs quickly and efficiently.

## Installation

```bash
pip install fastapi uvicorn
```

## Basic Example

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

## Running FastAPI

```bash
uvicorn main:app --reload
```

## Automatic Documentation

Swagger UI:

http://localhost:8000/docs

ReDoc:

http://localhost:8000/redoc

## Path Parameters

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

## Query Parameters

```python
@app.get("/items/")
def get_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

## Why FastAPI?

- Fast performance
- Automatic documentation
- Async support
- Type validation
- Easy development