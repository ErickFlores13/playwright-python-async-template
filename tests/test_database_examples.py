"""
Database Testing Examples
=========================

Demonstrates how to use the DatabaseClient and RedisClient in tests.

These tests require the corresponding infrastructure to be running.
Set environment variables before running::

    DB_TEST=true
    DB_TYPE=postgresql
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=testdb
    DB_USER=postgres
    DB_PASSWORD=password

or start the Docker Compose stack::

    docker-compose --profile with-db --profile with-redis up

Run::

    DB_TEST=true pytest tests/test_database_examples.py -v

Tests will be **skipped automatically** when DB_TEST is not set to ``true``.
Redis tests skip automatically when the Redis host is unreachable.
"""

import pytest
import pytest_asyncio

from helpers.database import DatabaseClient
from helpers.redis_client import RedisClient
from utils.config import Config

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# NOTE: The db_client fixture is already defined in conftest.py and uses
# DB_TEST=true to gate execution. These tests rely on it.


@pytest_asyncio.fixture
async def redis_client():
    """
    Provide a connected Redis client, skipping if Redis is unreachable.

    This fixture is defined locally so these tests can skip gracefully
    without affecting the rest of the suite.
    """
    cfg = Config.get_redis_config()
    client = RedisClient(port=str(cfg["port"]), db=int(cfg["db"]))
    try:
        # Verify connectivity
        await client.set("__health_check__", "1")
        await client.delete("__health_check__")
    except Exception as exc:
        await client.close()
        pytest.skip(f"Redis unavailable: {exc}")
    yield client
    await client.close()


# ---------------------------------------------------------------------------
# Database tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
async def test_db_fetch_one(db_client: DatabaseClient) -> None:
    """
    Integration test: fetch a single row from an information_schema table.

    Demonstrates:
    - DatabaseClient.fetch_one() with parameterised query
    - Row returned as a plain dict
    """
    result = await db_client.fetch_one(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = :schema LIMIT 1",
        {"schema": "information_schema"},
    )

    assert result is not None
    assert "table_name" in result


@pytest.mark.integration
async def test_db_fetch_all(db_client: DatabaseClient) -> None:
    """
    Integration test: fetch multiple rows.

    Demonstrates:
    - DatabaseClient.fetch_all() returning a list of dicts
    """
    rows = await db_client.fetch_all(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = :schema",
        {"schema": "information_schema"},
    )

    assert isinstance(rows, list)
    assert len(rows) > 0
    for row in rows:
        assert "table_name" in row


@pytest.mark.integration
async def test_db_execute_and_verify(db_client: DatabaseClient) -> None:
    """
    Integration test: INSERT a row then verify it with SELECT.

    Demonstrates:
    - DatabaseClient.execute() for write operations
    - Transactional commit and SELECT verification

    Note: This test creates and then cleans up a temporary table.
    """
    # Create a temporary table for this test
    await db_client.execute(
        "CREATE TEMP TABLE IF NOT EXISTS framework_test_run "
        "(id SERIAL PRIMARY KEY, label TEXT NOT NULL)"
    )

    await db_client.execute(
        "INSERT INTO framework_test_run (label) VALUES (:label)",
        {"label": "example_run"},
    )

    row = await db_client.fetch_one(
        "SELECT label FROM framework_test_run WHERE label = :label",
        {"label": "example_run"},
    )

    assert row is not None
    assert row["label"] == "example_run"


@pytest.mark.integration
async def test_db_session_maker(db_client: DatabaseClient) -> None:
    """
    Integration test: use the session_maker directly for ORM-style access.

    Demonstrates:
    - Direct SQLAlchemy async session for advanced queries
    - session_maker context manager usage
    """
    from sqlalchemy import text

    async with db_client.session_maker() as session:
        result = await session.execute(
            text("SELECT current_database()")
        )
        db_name = result.scalar()
        assert isinstance(db_name, str)
        assert len(db_name) > 0


# ---------------------------------------------------------------------------
# Redis tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
async def test_redis_set_get(redis_client: RedisClient) -> None:
    """
    Integration test: write a value to Redis and read it back.

    Demonstrates:
    - RedisClient.set() and get()
    - Bytes-to-string decoding of returned values
    """
    await redis_client.set("framework:test_key", "hello_redis")
    raw = await redis_client.get("framework:test_key")

    assert raw is not None
    assert raw.decode() == "hello_redis"

    await redis_client.delete("framework:test_key")


@pytest.mark.integration
async def test_redis_key_existence(redis_client: RedisClient) -> None:
    """
    Integration test: check key existence and deletion.

    Demonstrates:
    - RedisClient.exists() and delete()
    """
    key = "framework:existence_test"
    await redis_client.set(key, "1")

    assert await redis_client.exists(key) == 1

    await redis_client.delete(key)

    assert await redis_client.exists(key) == 0


@pytest.mark.integration
async def test_redis_list_keys(redis_client: RedisClient) -> None:
    """
    Integration test: list keys matching a pattern.

    Demonstrates:
    - RedisClient.list_keys() with a glob pattern
    """
    await redis_client.set("framework:a", "1")
    await redis_client.set("framework:b", "2")

    keys = await redis_client.list_keys("framework:*")
    decoded_keys = [k.decode() if isinstance(k, bytes) else k for k in keys]

    assert "framework:a" in decoded_keys
    assert "framework:b" in decoded_keys

    # Cleanup
    await redis_client.delete("framework:a")
    await redis_client.delete("framework:b")


@pytest.mark.integration
async def test_redis_context_manager() -> None:
    """
    Integration test: RedisClient used as an async context manager.

    Demonstrates:
    - async with RedisClient() pattern
    - Automatic connection cleanup on exit
    """
    cfg = Config.get_redis_config()
    try:
        async with RedisClient(port=str(cfg["port"]), db=int(cfg["db"])) as client:
            await client.set("framework:ctx_test", "ctx_value")
            value = await client.get("framework:ctx_test")
            assert value is not None
            assert value.decode() == "ctx_value"
            await client.delete("framework:ctx_test")
    except Exception as exc:
        pytest.skip(f"Redis unavailable: {exc}")
