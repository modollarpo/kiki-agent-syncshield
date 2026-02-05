"""
Graceful shutdown handler for KIKI Agent services
Ensures clean termination of connections and background tasks
"""

import signal
import asyncio
import logging
from typing import List, Callable, Optional
from contextlib import asynccontextmanager


logger = logging.getLogger(__name__)


class GracefulShutdownHandler:
    """
    Handles graceful shutdown of services.
    Registers cleanup functions and executes them on SIGTERM/SIGINT.
    """
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.cleanup_functions: List[Callable] = []
        self.shutdown_event = asyncio.Event()
        self._registered_signals = False
    
    def register_cleanup(self, cleanup_func: Callable):
        """Register a cleanup function to be called on shutdown"""
        self.cleanup_functions.append(cleanup_func)
    
    def register_signal_handlers(self):
        """Register signal handlers for graceful shutdown"""
        if self._registered_signals:
            return
        
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self._shutdown(s))
            )
        
        self._registered_signals = True
        logger.info("Registered graceful shutdown handlers for SIGTERM and SIGINT")
    
    async def _shutdown(self, sig):
        """Execute shutdown sequence"""
        logger.info(f"Received signal {sig.name}, initiating graceful shutdown...")
        
        # Set shutdown event
        self.shutdown_event.set()
        
        # Execute cleanup functions
        for i, cleanup_func in enumerate(self.cleanup_functions):
            try:
                logger.info(f"Executing cleanup function {i+1}/{len(self.cleanup_functions)}")
                if asyncio.iscoroutinefunction(cleanup_func):
                    await asyncio.wait_for(cleanup_func(), timeout=self.timeout)
                else:
                    cleanup_func()
            except asyncio.TimeoutError:
                logger.warning(f"Cleanup function {i+1} timed out after {self.timeout}s")
            except Exception as e:
                logger.error(f"Error in cleanup function {i+1}: {e}", exc_info=True)
        
        logger.info("Graceful shutdown complete")
    
    async def wait_for_shutdown(self):
        """Wait for shutdown signal"""
        await self.shutdown_event.wait()


@asynccontextmanager
async def lifespan_with_shutdown(app, shutdown_handler: GracefulShutdownHandler):
    """
    Lifespan context manager for FastAPI with graceful shutdown.
    
    Usage:
        shutdown_handler = GracefulShutdownHandler(timeout=30)
        app = FastAPI(lifespan=lambda app: lifespan_with_shutdown(app, shutdown_handler))
    """
    # Startup
    shutdown_handler.register_signal_handlers()
    logger.info(f"Starting {app.title}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {app.title}")
    await shutdown_handler._shutdown(signal.SIGTERM)


# Example cleanup functions for common resources

async def cleanup_database_pool(pool):
    """Cleanup database connection pool"""
    logger.info("Closing database connection pool")
    await pool.close()


async def cleanup_redis(redis_client):
    """Cleanup Redis connection"""
    logger.info("Closing Redis connection")
    await redis_client.close()


async def cleanup_http_client(client):
    """Cleanup HTTP client"""
    logger.info("Closing HTTP client")
    await client.aclose()


def cleanup_background_tasks(tasks: List[asyncio.Task]):
    """Cancel and cleanup background tasks"""
    logger.info(f"Cancelling {len(tasks)} background tasks")
    for task in tasks:
        if not task.done():
            task.cancel()
