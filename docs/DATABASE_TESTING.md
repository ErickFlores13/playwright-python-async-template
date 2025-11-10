# Database Testing Guide

Complete guide for database testing in this Playwright template. This template provides flexible database clients supporting SQL databases (PostgreSQL, MySQL, SQL Server, Oracle) and MongoDB.

---

## Table of Contents
1. [Quick Start](#quick-start)
2. [SQL Database Client](#sql-database-client)
3. [MongoDB Client](#mongodb-client)
4. [CRUD Operations](#crud-operations)
5. [Using SQLAlchemy ORM](#using-sqlalchemy-orm)
6. [Transactions](#transactions)
7. [Hybrid UI + Database Testing](#hybrid-ui--database-testing)
8. [Best Practices](#best-practices)

---

## Quick Start

### Basic Setup

**1. Configure `.env`:**
```bash
# Enable database testing
DB_TEST=true

# SQL Database Configuration
DB_TYPE=postgresql          # postgresql, mysql, mssql, oracle
DB_HOST=localhost
DB_PORT=5432
DB_NAME=testdb
DB_USER=postgres
DB_PASSWORD=password
```

**2. Use in Tests:**
```python
@pytest.mark.asyncio
async def test_database(db_client):
    # Query database
    user = await db_client.fetch_one(
        "SELECT * FROM users WHERE email = :email",
        {"email": "test@test.com"}
    )
    
    assert user is not None
    assert user["status"] == "active"
```

**3. See Examples:**
Check `tests/test_database_examples.py` for complete working examples of all database operations.

---

## SQL Database Client

The `DatabaseClient` provides a simple, flexible interface for SQL database operations. Write your own queries - the client handles connection, pooling, and execution.

### Supported Databases

- **PostgreSQL** (`postgresql`) - Default, recommended ⭐
- **MySQL** (`mysql`)
- **SQL Server** (`mssql`)
- **Oracle** (`oracle`)

### Connection Configuration

The client auto-configures from environment variables:

```python
# Automatic connection from .env
client = DatabaseClient()
await client.connect()
```

**Connection String Templates:**
```python
# PostgreSQL
postgresql+asyncpg://user:pass@host:5432/dbname

# MySQL
mysql+aiomysql://user:pass@host:3306/dbname

# SQL Server
mssql+aioodbc://user:pass@host:1433/dbname?driver=ODBC+Driver+17+for+SQL+Server

# Oracle
oracle+cx_oracle_async://user:pass@host:1521/dbname
```

---

## MongoDB Client

For NoSQL database operations, use the `MongoDBClient`:

### Configuration

```bash
# .env configuration
DB_TEST=true
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=testdb
MONGO_USER=
MONGO_PASSWORD=
```

### Basic Usage

```python
@pytest.mark.asyncio
async def test_mongodb(mongo_client):
    # Get collection
    users = mongo_client.collection("users")
    
    # Insert document
    result = await users.insert_one({
        "name": "John",
        "email": "john@example.com",
        "status": "active"
    })
    
    assert result.inserted_id is not None
```

---

## CRUD Operations

### Create (INSERT)

```python
@pytest.mark.asyncio
async def test_create_user(db_client):
    # Insert new record
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
    assert user["status"] == "active"
```

---

### Read (SELECT)

**Fetch Single Row:**
```python
@pytest.mark.asyncio
async def test_fetch_user(db_client):
    user = await db_client.fetch_one(
        "SELECT * FROM users WHERE id = :id",
        {"id": 1}
    )
    
    assert user is not None
    assert "username" in user
    assert "email" in user
```

**Fetch Multiple Rows:**
```python
@pytest.mark.asyncio
async def test_fetch_users(db_client):
    users = await db_client.fetch_all(
        "SELECT * FROM users WHERE status = :status",
        {"status": "active"}
    )
    
    assert len(users) > 0
    assert all(user["status"] == "active" for user in users)
```

**Fetch with Conditions:**
```python
@pytest.mark.asyncio
async def test_search_users(db_client):
    users = await db_client.fetch_all(
        """
        SELECT * FROM users 
        WHERE email LIKE :pattern 
        AND created_at > :date
        ORDER BY username
        """,
        {
            "pattern": "%@example.com",
            "date": "2024-01-01"
        }
    )
    
    assert all("@example.com" in user["email"] for user in users)
```

---

### Update (UPDATE)

```python
@pytest.mark.asyncio
async def test_update_user(db_client):
    # Update user status
    await db_client.execute(
        "UPDATE users SET status = :status WHERE email = :email",
        {
            "status": "inactive",
            "email": "test@example.com"
        }
    )
    
    # Verify update
    user = await db_client.fetch_one(
        "SELECT * FROM users WHERE email = :email",
        {"email": "test@example.com"}
    )
    
    assert user["status"] == "inactive"
```

**Update Multiple Fields:**
```python
@pytest.mark.asyncio
async def test_update_profile(db_client):
    await db_client.execute(
        """
        UPDATE users 
        SET username = :username, 
            phone = :phone,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :id
        """,
        {
            "username": "newusername",
            "phone": "+1234567890",
            "id": 1
        }
    )
```

---

### Delete (DELETE)

```python
@pytest.mark.asyncio
async def test_delete_user(db_client):
    # Delete user
    await db_client.execute(
        "DELETE FROM users WHERE email = :email",
        {"email": "test@example.com"}
    )
    
    # Verify deletion
    user = await db_client.fetch_one(
        "SELECT * FROM users WHERE email = :email",
        {"email": "test@example.com"}
    )
    
    assert user is None
```

---

## Using SQLAlchemy ORM

The `DatabaseClient` exposes the SQLAlchemy engine and session maker, allowing you to use the ORM directly.

### Define Models

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

---

### Use ORM in Tests

```python
@pytest.mark.asyncio
async def test_with_orm(db_client):
    from sqlalchemy import select
    
    # Use the session maker from db_client
    async with db_client.session_maker() as session:
        # Query with ORM
        stmt = select(User).where(User.email == "test@example.com")
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        assert user is not None
        assert user.status == "active"
```

**Create with ORM:**
```python
@pytest.mark.asyncio
async def test_create_with_orm(db_client):
    async with db_client.session_maker() as session:
        # Create new user
        new_user = User(
            username="ormuser",
            email="orm@example.com",
            status="active"
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        
        assert new_user.id is not None
```

**Complex Queries:**
```python
@pytest.mark.asyncio
async def test_complex_query(db_client):
    from sqlalchemy import select, and_, or_
    
    async with db_client.session_maker() as session:
        # Multiple conditions
        stmt = select(User).where(
            and_(
                User.status == "active",
                or_(
                    User.email.like("%@example.com"),
                    User.username.like("test%")
                )
            )
        ).order_by(User.created_at.desc())
        
        result = await session.execute(stmt)
        users = result.scalars().all()
        
        assert all(user.status == "active" for user in users)
```

---

## Transactions

### Manual Transaction Control

```python
@pytest.mark.asyncio
async def test_transaction(db_client):
    async with db_client.session_maker() as session:
        try:
            # Begin transaction
            await session.execute(
                text("INSERT INTO users (username, email) VALUES (:username, :email)"),
                {"username": "user1", "email": "user1@example.com"}
            )
            await session.execute(
                text("INSERT INTO users (username, email) VALUES (:username, :email)"),
                {"username": "user2", "email": "user2@example.com"}
            )
            
            # Commit transaction
            await session.commit()
        except Exception as e:
            # Rollback on error
            await session.rollback()
            raise
```

---

### Transaction Rollback for Test Isolation

```python
@pytest.mark.asyncio
async def test_with_rollback(db_client):
    async with db_client.session_maker() as session:
        async with session.begin():
            # All operations in this block
            await session.execute(
                text("INSERT INTO users (username, email) VALUES (:username, :email)"),
                {"username": "tempuser", "email": "temp@example.com"}
            )
            
            # Verify within transaction
            result = await session.execute(
                text("SELECT * FROM users WHERE email = :email"),
                {"email": "temp@example.com"}
            )
            user = result.fetchone()
            assert user is not None
            
            # Explicit rollback - cleanup
            await session.rollback()
        
        # Verify rollback - user should not exist
        result = await session.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {"email": "temp@example.com"}
        )
        user = result.fetchone()
        assert user is None
```

---

## Hybrid UI + Database Testing

Combine UI interactions with database verification for complete end-to-end testing.

### Verify UI Action in Database

```python
@pytest.mark.asyncio
async def test_registration_ui_db(page, db_client):
    # 1. Perform UI action
    await page.goto(f"{os.getenv('BASE_URL')}/register")
    await page.fill("#username", "newuser")
    await page.fill("#email", "newuser@example.com")
    await page.fill("#password", "SecurePass123!")
    await page.click("button[type='submit']")
    
    # Wait for success message
    await page.wait_for_selector(".success-message")
    
    # 2. Verify in database
    user = await db_client.fetch_one(
        "SELECT * FROM users WHERE email = :email",
        {"email": "newuser@example.com"}
    )
    
    assert user is not None
    assert user["username"] == "newuser"
    assert user["status"] == "pending"  # Default status
```

---

### Setup Test Data in Database

```python
@pytest.mark.asyncio
async def test_login_with_db_setup(page, db_client):
    # 1. Setup test data in database
    await db_client.execute(
        "INSERT INTO users (username, email, password_hash, status) VALUES (:u, :e, :p, :s)",
        {
            "u": "testuser",
            "e": "test@example.com",
            "p": "$2b$12$hashed_password",  # Pre-hashed password
            "s": "active"
        }
    )
    
    # 2. Test login via UI
    await page.goto(f"{os.getenv('BASE_URL')}/login")
    await page.fill("#username", "testuser")
    await page.fill("#password", "password123")
    await page.click("button[type='submit']")
    
    # 3. Verify successful login
    await page.wait_for_url("**/dashboard")
    assert await page.locator(".username").text_content() == "testuser"
    
    # 4. Cleanup
    await db_client.execute(
        "DELETE FROM users WHERE email = :email",
        {"email": "test@example.com"}
    )
```

---

### Verify UI Displays Database Data

```python
@pytest.mark.asyncio
async def test_profile_display(page, db_client):
    # 1. Insert user with known data
    await db_client.execute(
        """
        INSERT INTO users (username, email, phone, status) 
        VALUES (:username, :email, :phone, :status)
        """,
        {
            "username": "profiletest",
            "email": "profile@example.com",
            "phone": "+1234567890",
            "status": "active"
        }
    )
    
    # 2. Login and navigate to profile
    await page.goto(f"{os.getenv('BASE_URL')}/login")
    # ... login steps ...
    await page.goto(f"{os.getenv('BASE_URL')}/profile")
    
    # 3. Verify UI matches database
    ui_email = await page.text_content(".profile-email")
    ui_phone = await page.text_content(".profile-phone")
    
    assert ui_email == "profile@example.com"
    assert ui_phone == "+1234567890"
    
    # 4. Cleanup
    await db_client.execute(
        "DELETE FROM users WHERE email = :email",
        {"email": "profile@example.com"}
    )
```

---

### Test Data Modification via UI

```python
@pytest.mark.asyncio
async def test_update_profile(page, db_client):
    # 1. Setup initial data
    await db_client.execute(
        "INSERT INTO users (username, email, phone) VALUES (:u, :e, :p)",
        {"u": "updatetest", "e": "update@example.com", "p": "+1111111111"}
    )
    
    # 2. Login and update via UI
    # ... login steps ...
    await page.goto(f"{os.getenv('BASE_URL')}/profile/edit")
    await page.fill("#phone", "+9999999999")
    await page.click("button[type='submit']")
    
    # 3. Verify database updated
    user = await db_client.fetch_one(
        "SELECT * FROM users WHERE email = :email",
        {"email": "update@example.com"}
    )
    
    assert user["phone"] == "+9999999999"
    
    # 4. Cleanup
    await db_client.execute(
        "DELETE FROM users WHERE email = :email",
        {"email": "update@example.com"}
    )
```

---

## Best Practices

### ✅ DO

1. **Use parameterized queries (prevents SQL injection)**
```python
# Good - parameterized
user = await db_client.fetch_one(
    "SELECT * FROM users WHERE email = :email",
    {"email": email_input}
)
```

2. **Enable database testing explicitly**
```bash
# .env
DB_TEST=true  # Explicit opt-in
```

3. **Clean up test data**
```python
@pytest.mark.asyncio
async def test_with_cleanup(db_client):
    try:
        # Test operations
        await db_client.execute("INSERT INTO users ...")
        # ... test logic ...
    finally:
        # Always cleanup
        await db_client.execute("DELETE FROM users WHERE email = :email", {...})
```

4. **Use transactions for test isolation**
```python
async with db_client.session_maker() as session:
    async with session.begin():
        # Test operations
        # Auto-rollback on exception
```

5. **Verify database state after UI actions**
```python
# UI action
await page.click("#submit")

# Verify in database
record = await db_client.fetch_one("SELECT ...")
assert record is not None
```

---

### ❌ DON'T

1. **Don't use string concatenation (SQL injection risk)**
```python
# Bad - vulnerable to SQL injection
query = f"SELECT * FROM users WHERE email = '{email}'"  # ❌
result = await db_client.fetch_one(query)

# Good - parameterized
result = await db_client.fetch_one(
    "SELECT * FROM users WHERE email = :email",
    {"email": email}
)  # ✅
```

2. **Don't hardcode credentials**
```python
# Bad
client = DatabaseClient("postgresql://postgres:password@localhost/db")  # ❌

# Good - use environment variables
client = DatabaseClient()  # Auto-loads from .env ✅
```

3. **Don't leave test data in database**
```python
# Bad - no cleanup
await db_client.execute("INSERT INTO users ...")  # ❌

# Good - cleanup in finally
try:
    await db_client.execute("INSERT INTO users ...")
    # ... tests ...
finally:
    await db_client.execute("DELETE FROM users WHERE ...")  # ✅
```

4. **Don't test against production database**
```bash
# .env - use separate test database
DB_NAME=testdb  # ✅ Not production
```

5. **Don't run database tests when DB_TEST=false**
```python
# Tests auto-skip when DB_TEST is not true
# No need to manually check
```

---

## ⚠️ CI/CD Security Warning

**We strongly recommend NOT including database tests in CI/CD pipelines.**

### Security Risks:

1. **Credential Exposure**
   - Database credentials stored in CI/CD environment variables
   - Risk of credentials leaking in logs or build artifacts
   - Shared CI environments may expose secrets

2. **Network Exposure**
   - Opening database ports to CI runners
   - Potential attack vector if CI is compromised
   - Test databases may be accessible from internet

3. **Data Breach Risk**
   - Test data may contain sensitive information
   - CI logs may expose query results
   - Database dumps in artifacts could leak data

4. **Infrastructure Attack Surface**
   - Additional database containers/services = more attack vectors
   - Misconfigured database services in CI
   - Potential for SQL injection testing to affect shared resources

### Recommended Approach:

✅ **Run database tests locally only**
```bash
# Developer machine - secure, controlled environment
DB_TEST=true pytest tests/test_database_examples.py
```

✅ **Use separate test databases**
```bash
# Never use production or staging databases
DB_NAME=local_test_db  # Isolated test database
```

✅ **Keep database credentials out of CI**
```yaml
# CI configuration - skip database tests
environment:
  DB_TEST: false  # Database tests disabled in CI
```

✅ **If you MUST run in CI (advanced teams only):**
- Use ephemeral containers (Docker) that are destroyed after tests
- Use CI secrets management (GitHub Secrets, Jenkins Credentials)
- Rotate database credentials regularly
- Use network isolation (VPC, security groups)
- Never commit `.env` files with real credentials
- Audit CI logs for credential leaks

### Alternative: Mock/Integration Tests

Instead of real database tests in CI, consider:
- Mock database responses for unit tests
- Integration tests with in-memory databases (SQLite)
- Contract testing to verify database interface
- Schedule database tests nightly on secure infrastructure

**Bottom line:** Database testing in CI/CD introduces significant security risks. Keep it local unless you have dedicated DevOps/Security resources.

---

## Environment Variables Reference

```bash
# Enable/Disable Database Testing
DB_TEST=true                        # Set to 'true' to enable

# SQL Database (PostgreSQL, MySQL, SQL Server, Oracle)
DB_TYPE=postgresql                  # postgresql, mysql, mssql, oracle
DB_HOST=localhost
DB_PORT=5432                        # 5432 (Postgres), 3306 (MySQL), 1433 (SQL Server)
DB_NAME=testdb
DB_USER=postgres
DB_PASSWORD=password

# MongoDB
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=testdb
MONGO_USER=
MONGO_PASSWORD=
```

---

## Database Client Methods Reference

### SQL Database Client (`db_client`)

**Connection:**
- `connect()` - Establish connection
- `disconnect()` - Close connection and dispose pool

**Query Execution:**
- `execute(query, params)` - Execute INSERT, UPDATE, DELETE
- `fetch_one(query, params)` - Fetch single row as dictionary
- `fetch_all(query, params)` - Fetch all rows as list of dictionaries

**Direct Access:**
- `engine` - SQLAlchemy async engine
- `session_maker` - Session factory for ORM usage

---

### MongoDB Client (`mongo_client`)

**Connection:**
- `connect()` - Establish MongoDB connection
- `disconnect()` - Close MongoDB connection

**Collections:**
- `collection(name)` - Get collection by name

**Motor API:**
Use standard Motor/PyMongo async methods:
- `insert_one()`, `insert_many()`
- `find_one()`, `find()`
- `update_one()`, `update_many()`
- `delete_one()`, `delete_many()`

---

## Summary

This template provides **production-ready database testing** with:

✅ **Multi-Database Support** - PostgreSQL, MySQL, SQL Server, Oracle, MongoDB  
✅ **Flexible Querying** - Raw SQL or SQLAlchemy ORM  
✅ **Connection Pooling** - Optimized performance  
✅ **Async Operations** - Non-blocking database calls  
✅ **Hybrid Testing** - Combine UI + API + Database seamlessly  
✅ **Test Isolation** - Transaction support for cleanup  

**Philosophy:** Provide connection infrastructure, not business logic. You write the queries that match your schema and needs.

---

## Required Dependencies

Add to `requirements.txt`:

```txt
# Core database support
sqlalchemy[asyncio]>=2.0.0

# Database drivers (install only what you need)
asyncpg>=0.29.0              # PostgreSQL
aiomysql>=0.2.0              # MySQL
pyodbc>=5.0.0                # SQL Server
cx-Oracle>=8.3.0             # Oracle
motor>=3.3.0                 # MongoDB
```

---

**Next Steps:**
1. Set `DB_TEST=true` in `.env`
2. Configure your database connection
3. Write tests with your own queries
4. Run: `pytest tests/test_database_examples.py`
