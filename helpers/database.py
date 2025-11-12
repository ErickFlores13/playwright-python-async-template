"""
Database client for async database operations.
Supports: PostgreSQL, MySQL, SQL Server, Oracle

Provides basic connection infrastructure and query execution methods.
Users can write their own queries and choose their ORM (SQLAlchemy, raw SQL, etc.).

Author: Erick Guadalupe Félix Flores
License: MIT
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
import os


class DatabaseClient:
    """
    Async database client using SQLAlchemy.
    Provides basic connection and query execution methods.
    Users can write their own queries and choose their ORM.
    
    Supports multiple database types via connection string configuration:
    - PostgreSQL (postgresql+asyncpg)
    - MySQL (mysql+aiomysql)
    - SQL Server (mssql+aioodbc)
    - Oracle (oracle+cx_oracle_async)
    """
    
    def __init__(self, connection_string: Optional[str] = None) -> None:
        """
        Initialize database client.
        
        Args:
            connection_string: Database connection string. If None, builds from env vars.
        """
        self.connection_string = connection_string or self._build_connection_string()
        self.engine = None
        self.session_maker = None
    
    def _build_connection_string(self) -> str:
        """Build connection string from environment variables."""
        db_type = os.getenv("DB_TYPE", "postgresql")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        database = os.getenv("DB_NAME", "testdb")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "password")
        
        # Connection string templates for different databases
        templates = {
            "postgresql": f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}",
            "mysql": f"mysql+aiomysql://{user}:{password}@{host}:{port}/{database}",
            "mssql": f"mssql+aioodbc://{user}:{password}@{host}:{port}/{database}?driver=ODBC+Driver+17+for+SQL+Server",
            "oracle": f"oracle+cx_oracle_async://{user}:{password}@{host}:{port}/{database}",
        }
        
        return templates.get(db_type, templates["postgresql"])
    
    async def connect(self) -> None:
        """Establish database connection with connection pooling."""
        self.engine = create_async_engine(
            self.connection_string,
            echo=False,
            pool_size=5,
            max_overflow=10
        )
        self.session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def disconnect(self) -> None:
        """Close database connection and dispose of connection pool."""
        if self.engine:
            await self.engine.dispose()
    
    async def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute a query (INSERT, UPDATE, DELETE).
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            Result of the execution
            
        Example:
            await db.execute(
                "INSERT INTO users (username, email) VALUES (:username, :email)",
                {"username": "test", "email": "test@test.com"}
            )
        """
        async with self.session_maker() as session:
            result = await session.execute(text(query), params or {})
            await session.commit()
            return result
    
    async def fetch_one(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row from database.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            Single row as dictionary or None
            
        Example:
            user = await db.fetch_one(
                "SELECT * FROM users WHERE email = :email",
                {"email": "test@test.com"}
            )
        """
        async with self.session_maker() as session:
            result = await session.execute(text(query), params or {})
            row = result.fetchone()
            if row:
                return dict(row._mapping)
            return None
    
    async def fetch_all(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Fetch all rows from database.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            List of rows as dictionaries
            
        Example:
            users = await db.fetch_all(
                "SELECT * FROM users WHERE status = :status",
                {"status": "active"}
            )
        """
        async with self.session_maker() as session:
            result = await session.execute(text(query), params or {})
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]
