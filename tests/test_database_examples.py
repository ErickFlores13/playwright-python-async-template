"""
Database Testing Examples

Simple examples showing how to use the database clients in this template:
- SQL Database operations (PostgreSQL, MySQL, SQL Server, Oracle)
- Hybrid UI + Database testing

Setup:
1. Set DB_TEST=true in .env
2. Configure database connection (DB_TYPE, DB_HOST, DB_PORT, etc.)
3. Run: pytest tests/test_database_examples.py
"""

import pytest
import os
from helpers.database import DatabaseClient


# ============================================================================
# Example 1: Basic SELECT Query
# ============================================================================
@pytest.mark.asyncio
async def test_fetch_single_record(db_client: DatabaseClient):
    """
    Fetch a single record from the database.
    
    This is the most common database operation - querying data.
    """
    user = await db_client.fetch_one(
        "SELECT * FROM users WHERE id = :id",
        {"id": 1}
    )
    
    # user is a dictionary: {"id": 1, "username": "...", "email": "..."}
    assert user is not None
    assert "username" in user
    assert "email" in user


# ============================================================================
# Example 2: Fetch Multiple Records
# ============================================================================
@pytest.mark.asyncio
async def test_fetch_multiple_records(db_client: DatabaseClient):
    """
    Fetch multiple records matching a condition.
    """
    active_users = await db_client.fetch_all(
        "SELECT * FROM users WHERE status = :status",
        {"status": "active"}
    )
    
    # active_users is a list of dictionaries
    assert len(active_users) >= 0
    assert all(user["status"] == "active" for user in active_users)


# ============================================================================
# Example 3: INSERT New Record
# ============================================================================
@pytest.mark.asyncio
async def test_insert_record(db_client: DatabaseClient):
    """
    Insert a new record into the database.
    
    Remember to clean up test data!
    """
    # Insert
    await db_client.execute(
        "INSERT INTO users (username, email, status) VALUES (:username, :email, :status)",
        {
            "username": "testuser",
            "email": "test@example.com",
            "status": "active"
        }
    )
    
    # Verify insertion
    user = await db_client.fetch_one(
        "SELECT * FROM users WHERE email = :email",
        {"email": "test@example.com"}
    )
    assert user["username"] == "testuser"
    
    # Cleanup
    await db_client.execute(
        "DELETE FROM users WHERE email = :email",
        {"email": "test@example.com"}
    )


# ============================================================================
# Example 4: UPDATE Record
# ============================================================================
@pytest.mark.asyncio
async def test_update_record(db_client: DatabaseClient):
    """
    Update an existing record.
    """
    # First, create a test record
    await db_client.execute(
        "INSERT INTO users (username, email, status) VALUES (:u, :e, :s)",
        {"u": "updatetest", "e": "update@example.com", "s": "active"}
    )
    
    # Update the record
    await db_client.execute(
        "UPDATE users SET status = :status WHERE email = :email",
        {"status": "inactive", "email": "update@example.com"}
    )
    
    # Verify update
    user = await db_client.fetch_one(
        "SELECT * FROM users WHERE email = :email",
        {"email": "update@example.com"}
    )
    assert user["status"] == "inactive"
    
    # Cleanup
    await db_client.execute(
        "DELETE FROM users WHERE email = :email",
        {"email": "update@example.com"}
    )


# ============================================================================
# Example 5: DELETE Record
# ============================================================================
@pytest.mark.asyncio
async def test_delete_record(db_client: DatabaseClient):
    """
    Delete a record from the database.
    """
    # Create test record
    await db_client.execute(
        "INSERT INTO users (username, email) VALUES (:u, :e)",
        {"u": "deletetest", "e": "delete@example.com"}
    )
    
    # Delete the record
    await db_client.execute(
        "DELETE FROM users WHERE email = :email",
        {"email": "delete@example.com"}
    )
    
    # Verify deletion
    user = await db_client.fetch_one(
        "SELECT * FROM users WHERE email = :email",
        {"email": "delete@example.com"}
    )
    assert user is None


# ============================================================================
# Example 6: Using SQLAlchemy ORM (Advanced)
# ============================================================================
@pytest.mark.asyncio
async def test_with_sqlalchemy_orm(db_client: DatabaseClient):
    """
    Use SQLAlchemy ORM directly with the db_client.
    
    The db_client exposes the session_maker for ORM usage.
    """
    from sqlalchemy import text
    
    async with db_client.session_maker() as session:
        # Execute query using SQLAlchemy
        result = await session.execute(
            text("SELECT * FROM users WHERE status = :status"),
            {"status": "active"}
        )
        users = result.fetchall()
        
        assert len(users) >= 0


# ============================================================================
# Example 7: Hybrid UI + Database (Most Powerful)
# ============================================================================
@pytest.mark.asyncio
async def test_ui_database_verification(page, db_client: DatabaseClient):
    """
    Combine UI testing with database verification.
    
    This is one of the most powerful testing patterns:
    1. Perform action in UI
    2. Verify result in database
    """
    # Example: User registration
    await page.goto(f"{os.getenv('BASE_URL')}/register")
    await page.fill("#username", "uitest")
    await page.fill("#email", "uitest@example.com")
    await page.fill("#password", "SecurePass123!")
    await page.click("button[type='submit']")
    
    # Wait for success (adjust selector for your app)
    # await page.wait_for_selector(".success-message")
    
    # Verify user exists in database
    user = await db_client.fetch_one(
        "SELECT * FROM users WHERE email = :email",
        {"email": "uitest@example.com"}
    )
    
    assert user is not None
    assert user["username"] == "uitest"
    
    # Cleanup
    await db_client.execute(
        "DELETE FROM users WHERE email = :email",
        {"email": "uitest@example.com"}
    )


# ============================================================================
# Example 11: Setup Test Data in Database
# ============================================================================
@pytest.mark.asyncio
async def test_setup_data_for_ui_test(page, db_client: DatabaseClient):
    """
    Setup test data in database, then test UI.
    
    This is useful when you need specific data for testing.
    """
    # Setup test user in database
    await db_client.execute(
        "INSERT INTO users (username, email, password_hash, status) VALUES (:u, :e, :p, :s)",
        {
            "u": "presetuser",
            "e": "preset@example.com",
            "p": "$2b$12$hashed_password_here",  # Pre-hashed password
            "s": "active"
        }
    )
    
    # Test login with this user
    await page.goto(f"{os.getenv('BASE_URL')}/login")
    await page.fill("#username", "presetuser")
    await page.fill("#password", "password123")
    await page.click("button[type='submit']")
    
    # Verify login success (adjust for your app)
    # await page.wait_for_url("**/dashboard")
    
    # Cleanup
    await db_client.execute(
        "DELETE FROM users WHERE email = :email",
        {"email": "preset@example.com"}
    )


# ============================================================================
# NOTES FOR USERS:
# ============================================================================
"""
Configuration Required (.env):
    DB_TEST=true                    # Enable database testing
    DB_TYPE=postgresql              # postgresql, mysql, mssql, oracle
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=testdb
    DB_USER=postgres
    DB_PASSWORD=password

How to Run:
    # Run all database tests
    DB_TEST=true pytest tests/test_database_examples.py
    
    # Run specific test
    DB_TEST=true pytest tests/test_database_examples.py::test_fetch_single_record
    
    # Run without database (tests will be skipped)
    pytest tests/test_database_examples.py

Key Points:
    1. Always use parameterized queries (prevents SQL injection)
    2. Clean up test data in finally blocks or at end of test
    3. Use transactions for test isolation (advanced)
    4. Write your own queries based on your schema
    5. Choose raw SQL or SQLAlchemy ORM based on your needs

Dependencies (add to requirements.txt):
    sqlalchemy[asyncio]>=2.0.0
    asyncpg>=0.29.0           # PostgreSQL
    aiomysql>=0.2.0           # MySQL
    pyodbc>=5.0.0             # SQL Server
    cx-Oracle>=8.3.0          # Oracle
"""
