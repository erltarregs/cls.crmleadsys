# app/db/session.py

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text
from app.core.config import settings

# -- Async Engine (asyncpg driver) -------------
# 
# This engine uses asyncpg under the hood.
# The URL prefix "postgresql+asyncpg://" tells SQLAlchemy which driver to use.
# 
# pool_size     - number of persistent connections kept open
# max_overflow  - extra connections allowed beyond pool_size under heavy load
# pool_pre_ping - before using a connection, send a lightweight "SELECT 1"
#                 to verify it's still active (handles server-side timeouts)
# 
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size = 5,
    max_overflow = 10,
    pool_pre_ping = True,
    echo = settings.DEBUG, # logs every SQL statement when DEBUG=True
)

# -- Session Factory --------------
# 
# AsyncSessionLocal is a factory - calling it creates a new AsyncSession.
# expire_on_commit=False means objects remain usable after a commit
# without needing another DB roundtrip to refresh them.

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# -- Dependency (used in FastAPI routes) -------------
# 
# This is a FastAPI "dependency" - a function that FastAPI calls
# automatically before each request and cleans up after.
# 
# Usage in a route:
#   async def get_leads(db: AsyncSession = Depends(get_db)):
#       ...
# 
async def get_db() -> AsyncSession:
    """
    Yields a database session for a single request, then closes it.
    The try/finally ensures the session closes even if an exception occurs.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            