# Database Testing Guide

Complete guide for database and cache testing using the Playwright Python Async Framework.

---

## Table of Contents

- [Overview](#overview)
- [Supported Databases](#supported-databases)
- [Quick Start](#quick-start)
- [DatabaseClient API](#databaseclient-api)
- [Redis Testing](#redis-testing)
- [Docker Setup](#docker-setup)
- [Configuration Reference](#configuration-reference)
- [Complete Examples](#complete-examples)

---

## Overview

The framework ships with two helper clients:

| Client | Module | Purpose |
|--------|--------|---------|
| `DatabaseClient` | `helpers/database.py` | PostgreSQL, MySQL, SQL Server, Oracle |
| `RedisClient` | `helpers/redis_client.py` | Redis cache operations |

Both clients are **async-first** and integrate with pytest via fixtures defined
in `conftest.py`.

---

## Supported Databases

The `DatabaseClient` uses **SQLAlchemy async** drivers:

| Database | `DB_TYPE` value | Driver package |
|----------|----------------|----------------|
| PostgreSQL | `postgresql` | `asyncpg` (included) |
| MySQL | `mysql` | `aiomysql` (included) |
| SQL Server | `mssql` | `aioodbc` (install separately) |
| Oracle | `oracle` | `cx_oracle_async` (install separately) |

---

## Quick Start

### 1. Enable Database Testing

Set environment variables in `.env`:

```bash
DB_TEST=true
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=testdb
DB_USER=postgres
DB_PASSWORD=password
```

### 2. Use the `db_client` Fixture

The `db_client` fixture is defined in `conftest.py`. Tests that use it will
**skip automatically** when `DB_TEST` is not `true`:

```python
async def test_user_exists(db_client):
    user = await db_client.fetch_one(
        "SELECT * FROM users WHERE email = :email",
        {"email": "qa@example.com"},
    )
    assert user is not None
    assert user["status"] == "active"
```

### 3. Start Infrastructure (Optional)

Use Docker Compose for a ready-to-go database:

```bash
docker-compose --profile with-db up --abort-on-container-exit
```

---

## DatabaseClient API

### `fetch_one(query, params)` → `dict | None`

Fetch a single row as a dictionary. Returns `None` if no rows match.

```python
user = await db_client.fetch_one(
    "SELECT id, name, email, status FROM users WHERE id = :id",
    {"id": 42},
)
assert user is not None
assert user["status"] == "active"
```

### `fetch_all(query, params)` → `list[dict]`

Fetch all matching rows as a list of dictionaries.

```python
active_users = await db_client.fetch_all(
    "SELECT id, name FROM users WHERE status = :status",
    {"status": "active"},
)
assert len(active_users) > 0
```

### `execute(query, params)` → result

Execute an INSERT, UPDATE, or DELETE statement. Commits automatically.

```python
await db_client.execute(
    "UPDATE users SET status = :status WHERE id = :id",
    {"status": "inactive", "id": 42},
)
```

### `session_maker()` — SQLAlchemy session

For advanced ORM queries use the async session context manager directly:

```python
from sqlalchemy import text, select
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

class User(DeclarativeBase):
    __tablename__ = "users"
    id:     Mapped[int] = mapped_column(primary_key=True)
    name:   Mapped[str]
    email:  Mapped[str]
    status: Mapped[str]

async def test_orm_query(db_client):
    async with db_client.session_maker() as session:
        result = await session.execute(
            select(User).where(User.status == "active").limit(10)
        )
        users = result.scalars().all()
        assert len(users) > 0
```

---

## Redis Testing

### Configuration

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### Using `RedisClient` in Tests

```python
from helpers.redis_client import RedisClient
from utils.config import Config

@pytest_asyncio.fixture
async def redis():
    cfg = Config.get_redis_config()
    async with RedisClient(port=str(cfg["port"]), db=int(cfg["db"])) as client:
        yield client
```

### RedisClient API

```python
# Basic operations
await client.set("key", "value")
raw = await client.get("key")           # Returns bytes or None
value = raw.decode() if raw else None

await client.delete("key")             # Returns count deleted
exists = await client.exists("key")    # Returns 1 or 0

# List keys
keys = await client.list_keys("prefix:*")

# Bulk get
values = await client.mget(["key1", "key2", "key3"])

# Context manager (auto-close)
async with RedisClient() as client:
    await client.set("temp", "value")
```

---

## Docker Setup

Start all services with Docker Compose:

```bash
# Start everything (tests + PostgreSQL + Redis)
docker-compose --profile with-db --profile with-redis up --abort-on-container-exit

# PostgreSQL only
docker-compose --profile with-db up --abort-on-container-exit

# Redis only
docker-compose --profile with-redis up --abort-on-container-exit

# Tests without external services
docker-compose up --abort-on-container-exit

# Cleanup
docker-compose down -v
```

---

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_TEST` | `false` | Set `true` to enable database tests |
| `DB_TYPE` | `postgresql` | `postgresql` \| `mysql` \| `mssql` \| `oracle` |
| `DB_HOST` | `localhost` | Database host |
| `DB_PORT` | `5432` | Database port |
| `DB_NAME` | `testdb` | Database name |
| `DB_USER` | `postgres` | Database username |
| `DB_PASSWORD` | `password` | Database password |
| `REDIS_HOST` | `localhost` | Redis host |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_DB` | `0` | Redis database number (0–15) |

---

## Complete Examples

### Example 1: Data Integrity Validation

```python
async def test_order_creates_inventory_record(db_client):
    """After creating an order via UI/API, verify database state."""
    order_id = "ORD-2024-001"

    # Verify order exists
    order = await db_client.fetch_one(
        "SELECT * FROM orders WHERE order_ref = :ref",
        {"ref": order_id},
    )
    assert order is not None
    assert order["status"] == "pending"

    # Verify inventory was decremented
    inv = await db_client.fetch_one(
        "SELECT stock_count FROM inventory WHERE product_id = :pid",
        {"pid": order["product_id"]},
    )
    assert inv["stock_count"] >= 0
```

### Example 2: Test Data Setup and Teardown

```python
import pytest

@pytest.fixture
async def test_user(db_client):
    """Create a user for the test and remove it afterwards."""
    await db_client.execute(
        "INSERT INTO users (name, email, status) VALUES (:name, :email, :status)",
        {"name": "Test User", "email": "test_fixture@example.com", "status": "active"},
    )
    user = await db_client.fetch_one(
        "SELECT * FROM users WHERE email = :email",
        {"email": "test_fixture@example.com"},
    )
    yield user
    await db_client.execute(
        "DELETE FROM users WHERE id = :id",
        {"id": user["id"]},
    )

async def test_user_profile(db_client, test_user):
    """Test using the pre-created test user."""
    fetched = await db_client.fetch_one(
        "SELECT * FROM users WHERE id = :id",
        {"id": test_user["id"]},
    )
    assert fetched["name"] == "Test User"
```

### Example 3: Redis Cache Verification

```python
async def test_session_stored_in_redis(redis_client, page, login):
    """After login, verify that the session token is cached in Redis."""
    from utils.config import Config

    await login(Config.get_test_username(), Config.get_test_password(), Config.get_base_url())

    # Extract token from browser storage
    token = await page.evaluate("localStorage.getItem('authToken')")
    assert token

    # Verify Redis has the session
    session_data = await redis_client.get(f"session:{token}")
    assert session_data is not None
    assert json.loads(session_data.decode())["user_id"] > 0
```

### Example 4: Cross-Layer Validation (UI + DB)

```python
async def test_registration_persists_to_database(page, db_client):
    """Register via UI, then confirm the user exists in the database."""
    from tests.test_ui_examples import RegistrationPage
    from utils.test_helpers import TestDataGenerator

    email = TestDataGenerator.random_email()

    reg = RegistrationPage(page)
    await page.goto('https://app.example.com/register')
    await reg.register(email=email)
    await reg.validation.assert_visible('#successBanner')

    # Cross-check with database
    user = await db_client.fetch_one(
        "SELECT id, email, status FROM users WHERE email = :email",
        {"email": email},
    )
    assert user is not None
    assert user["status"] == "active"
```

---

See the `tests/test_database_examples.py` file for runnable examples.
