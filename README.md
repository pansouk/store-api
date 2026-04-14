# Store API

A lightweight REST API for managing posts and comments, built with FastAPI and async SQLite.

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Data Models](#data-models)
- [Database](#database)
- [Testing](#testing)

---

## Overview

Store API is a FastAPI application demonstrating modern Python web development patterns:
- Async database access with `databases` + `aiosqlite`
- Environment-based configuration with `pydantic-settings`
- Schema validation with Pydantic
- Full test coverage with async pytest fixtures

The domain is a simple post-and-comment system. There is no authentication — all endpoints are publicly accessible.

---

## Tech Stack

| Component | Library | Version |
|---|---|---|
| Framework | FastAPI | >=0.135.3 |
| ASGI Server | Uvicorn | >=0.44.0 |
| Database | SQLite (via aiosqlite) | - |
| Async DB client | databases | >=0.9.0 |
| SQL schema | SQLAlchemy (Core) | >=2.0.49 |
| Validation / Config | Pydantic / pydantic-settings | >=2.13.1 |
| Env vars | python-dotenv | >=1.2.2 |
| Testing | pytest + httpx | >=9.0.3 / >=0.28.1 |
| Package manager | uv | - |

---

## Project Structure

```
store-api/
├── main.py              # App factory, lifespan, router registration
├── config.py            # Environment-based configuration (dev/test/prod)
├── database.py          # SQLAlchemy table definitions, engine, async DB instance
├── models/
│   └── post.py          # Pydantic request/response schemas
├── routers/
│   └── post.py          # All route handlers
├── tests/
│   ├── conftest.py      # Shared pytest fixtures
│   └── routers/
│       └── test_post.py # Integration tests for post & comment endpoints
├── .env                 # Local environment variables (not committed)
├── .env.example         # Environment variable template
├── pyproject.toml       # Project metadata and dependencies
└── uv.lock              # Locked dependency tree
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)

### Installation

```bash
git clone <repo-url>
cd store-api
uv sync
```

### Environment Setup

Copy the example env file and configure it:

```bash
cp .env.example .env
```

Minimum required contents for development:

```dotenv
ENV_STATE=dev
DEV_DATABASE_URL=sqlite:///data.db
```

### Running the Server

```bash
uv run uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

Interactive docs: `http://localhost:8000/docs`

---

## Configuration

Configuration is managed in [config.py](config.py) using `pydantic-settings`. The environment is selected via `ENV_STATE` in `.env`.

| Environment | Config Class | Database | Force Rollback |
|---|---|---|---|
| `dev` | `DevConfig` | `sqlite:///data.db` | No |
| `test` | `TestConfig` | `sqlite:///test.db` | Yes |
| `prod` | `ProdConfig` | _(set via env)_ | No |

Each environment reads its own prefixed variables from `.env`:

```dotenv
# Development
ENV_STATE=dev
DEV_DATABASE_URL=sqlite:///data.db

# Test
ENV_STATE=test
TEST_DATABASE_URL=sqlite:///test.db
TEST_DB_FORCE_ROLL_BACK=true
```

**`DB_FORCE_ROLL_BACK`** — when `true`, every database query is automatically rolled back after it runs. This is used in the test environment to keep tests isolated without needing to truncate tables.

---

## API Reference

Base URL: `http://localhost:8000`

### Posts

#### Create a Post

```
POST /post
```

**Request body**

```json
{ "body": "Post content here" }
```

**Response** `201 Created`

```json
{ "id": 1, "body": "Post content here" }
```

---

#### List All Posts

```
GET /post
```

**Response** `200 OK`

```json
[
  { "id": 1, "body": "First post" },
  { "id": 2, "body": "Second post" }
]
```

---

#### Get Post with Comments

```
GET /post/{post_id}
```

**Path parameter:** `post_id` — integer ID of the post

**Response** `200 OK`

```json
{
  "post": { "id": 1, "body": "Post content here" },
  "comments": [
    { "id": 1, "body": "Nice post!", "post_id": 1 }
  ]
}
```

**Error** `404 Not Found` — when the post does not exist

---

### Comments

#### Create a Comment

```
POST /comment
```

**Request body**

```json
{ "body": "Comment text", "post_id": 1 }
```

**Response** `201 Created`

```json
{ "id": 1, "body": "Comment text", "post_id": 1 }
```

**Error** `404 Not Found` — when the referenced post does not exist

---

#### List Comments on a Post

```
GET /post/{post_id}/comment
```

**Path parameter:** `post_id` — integer ID of the post

**Response** `200 OK`

```json
[
  { "id": 1, "body": "Nice post!", "post_id": 1 },
  { "id": 2, "body": "Agreed!", "post_id": 1 }
]
```

---

## Data Models

Defined in [models/post.py](models/post.py).

```
UserPostIn       body: str
     |
     v
UserPost         id: int, body: str           (response)

CommentIn        body: str, post_id: int
     |
     v
Comment          id: int, body: str, post_id: int   (response)

UserPostWithComments
    post:     UserPost
    comments: list[Comment]                   (response)
```

All response schemas use Pydantic's `from_attributes=True` so they can be constructed directly from SQLAlchemy row objects.

---

## Database

Defined in [database.py](database.py).

SQLAlchemy Core (not ORM) is used to define the schema. Two tables are created at import time via `metadata.create_all(engine)`.

**posts**

| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary key |
| `body` | String | - |

**comments**

| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary key |
| `body` | String | - |
| `post_id` | Integer | FK → `posts.id`, Not Null |

Queries are executed via an async `databases.Database` instance, which wraps aiosqlite. The database connects on app startup and disconnects on shutdown via the FastAPI lifespan context manager in [main.py](main.py).

---

## Testing

Tests live in [tests/routers/test_post.py](tests/routers/test_post.py) and use `httpx.AsyncClient` with FastAPI's `ASGITransport` for full integration testing without a live server.

### Running Tests

```bash
uv run pytest
```

### Test Isolation

The test environment sets `DB_FORCE_ROLL_BACK=True`, which wraps every query in a transaction that is rolled back immediately. This means:
- No data persists between tests
- A separate `test.db` file is used, keeping development data untouched
- No table truncation or teardown logic is needed

### Test Fixtures

| Fixture | Scope | Purpose |
|---|---|---|
| `async_client` | function | Provides an `AsyncClient` wired to the app |
| `db` | function (autouse) | Connects & disconnects the database per test |
| `created_post` | function | Creates a post and returns its JSON |
| `created_comment` | function | Creates a comment on `created_post` and returns its JSON |

### Test Coverage

| Test | Endpoint | Scenario |
|---|---|---|
| `test_create_post` | `POST /post` | Happy path — 201 with correct body |
| `test_create_post_missing_data` | `POST /post` | Missing `body` field — 422 |
| `test_get_all_posts` | `GET /post` | Returns list containing created post |
| `test_create_comment` | `POST /comment` | Happy path — 201 with correct body |
| `test_get_comments_on_post` | `GET /post/{id}/comment` | Returns list with created comment |
| `test_get_comments_on_post_empty` | `GET /post/{id}/comment` | Returns empty list when no comments |
| `test_get_post_with_comments` | `GET /post/{id}` | Returns post with its comments |
| `test_get_missing_post_with_comments` | `GET /post/{id}` | Non-existent post — 404 |
