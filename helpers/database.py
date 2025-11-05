from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager

Base = declarative_base()

class AsyncPostgresConnector:
    def __init__(self, user, password, host, port, dbname, echo=False):
        self.db_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"
        self.engine = create_async_engine(self.db_url, echo=echo)
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            autoflush=False,
            autocommit=False,
        )

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def get_session(self):
        async with self.SessionLocal() as session:
            yield session
