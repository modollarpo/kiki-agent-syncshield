"""
Database connection pooling utilities for KIKI Agent services
Implements SQLAlchemy async pool with health checks
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from typing import Optional, AsyncGenerator
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class DatabasePool:
    """
    Async database connection pool manager with health checks.
    Quick Win #6: Database Connection Pooling
    """
    
    def __init__(
        self,
        database_url: str,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False
    ):
        """
        Initialize database pool.
        
        Args:
            database_url: Database connection string
            pool_size: Number of connections to maintain
            max_overflow: Maximum overflow connections beyond pool_size
            pool_timeout: Seconds to wait for connection from pool
            pool_recycle: Seconds after which connections are recycled
            echo: Enable SQL query logging
        """
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        
        # Create async engine with connection pooling
        self.engine = create_async_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,  # Verify connections before using
            echo=echo
        )
        
        # Create session factory
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info(
            f"Database pool initialized: size={pool_size}, "
            f"max_overflow={max_overflow}, timeout={pool_timeout}s"
        )
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session from pool"""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> bool:
        """
        Check database connection health.
        Returns True if database is accessible.
        """
        try:
            async with self.engine.connect() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def get_pool_status(self) -> dict:
        """Get current pool status for monitoring"""
        pool = self.engine.pool
        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total_connections": pool.size() + pool.overflow()
        }
    
    async def close(self):
        """Close all connections in pool"""
        logger.info("Closing database connection pool")
        await self.engine.dispose()


# Singleton instance for shared pool
_db_pool: Optional[DatabasePool] = None


def init_db_pool(
    database_url: str,
    pool_size: int = 10,
    max_overflow: int = 20,
    pool_timeout: int = 30,
    pool_recycle: int = 3600
) -> DatabasePool:
    """Initialize global database pool"""
    global _db_pool
    if _db_pool is not None:
        logger.warning("Database pool already initialized")
        return _db_pool
    
    _db_pool = DatabasePool(
        database_url=database_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle
    )
    return _db_pool


def get_db_pool() -> DatabasePool:
    """Get global database pool instance"""
    if _db_pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db_pool() first.")
    return _db_pool


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions"""
    pool = get_db_pool()
    async with pool.get_session() as session:
        yield session
