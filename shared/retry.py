"""
Retry logic with exponential backoff for KIKI Agent services
Quick Win #7: Implements intelligent retry strategies
"""

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)
import logging
from typing import Callable, Type, Tuple
from functools import wraps
import httpx

logger = logging.getLogger(__name__)


# Common retry configurations
RETRY_CONFIG_DEFAULT = {
    "stop": stop_after_attempt(3),
    "wait": wait_exponential(multiplier=1, min=1, max=10),
    "before_sleep": before_sleep_log(logger, logging.WARNING),
    "after": after_log(logger, logging.INFO)
}

RETRY_CONFIG_AGGRESSIVE = {
    "stop": stop_after_attempt(5),
    "wait": wait_exponential(multiplier=2, min=1, max=60),
    "before_sleep": before_sleep_log(logger, logging.WARNING),
    "after": after_log(logger, logging.INFO)
}

RETRY_CONFIG_CONSERVATIVE = {
    "stop": stop_after_attempt(2),
    "wait": wait_exponential(multiplier=1, min=2, max=5),
    "before_sleep": before_sleep_log(logger, logging.WARNING),
    "after": after_log(logger, logging.INFO)
}


def retry_on_http_error(
    max_attempts: int = 3,
    backoff_multiplier: float = 2.0,
    max_delay: int = 60,
    retry_status_codes: Tuple[int, ...] = (429, 500, 502, 503, 504)
):
    """
    Retry decorator for HTTP requests with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        backoff_multiplier: Exponential backoff multiplier
        max_delay: Maximum delay between retries in seconds
        retry_status_codes: HTTP status codes that should trigger retry
    
    Usage:
        @retry_on_http_error(max_attempts=5)
        async def fetch_data(url: str):
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
    """
    def should_retry(exception):
        if isinstance(exception, httpx.HTTPStatusError):
            return exception.response.status_code in retry_status_codes
        if isinstance(exception, (httpx.TimeoutException, httpx.ConnectError)):
            return True
        return False
    
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=backoff_multiplier, min=1, max=max_delay),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TimeoutException, httpx.ConnectError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO),
        reraise=True
    )


def retry_on_exception(
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    max_attempts: int = 3,
    backoff_multiplier: float = 1.0,
    max_delay: int = 10
):
    """
    Generic retry decorator for any exception types.
    
    Args:
        exception_types: Tuple of exception types to retry on
        max_attempts: Maximum number of retry attempts
        backoff_multiplier: Exponential backoff multiplier
        max_delay: Maximum delay between retries in seconds
    
    Usage:
        @retry_on_exception(
            exception_types=(ConnectionError, TimeoutError),
            max_attempts=5
        )
        def unreliable_operation():
            # ... operation that might fail
            pass
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=backoff_multiplier, min=1, max=max_delay),
        retry=retry_if_exception_type(exception_types),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO),
        reraise=True
    )


def retry_database_operation(max_attempts: int = 3):
    """
    Retry decorator specifically for database operations.
    Handles common database errors like connection timeouts.
    
    Usage:
        @retry_database_operation(max_attempts=5)
        async def save_user(user_data: dict):
            async with get_db_session() as session:
                session.add(User(**user_data))
                await session.commit()
    """
    from sqlalchemy.exc import OperationalError, DBAPIError
    
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=2, min=1, max=10),
        retry=retry_if_exception_type((OperationalError, DBAPIError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO),
        reraise=True
    )


def retry_service_call(service_name: str, max_attempts: int = 3):
    """
    Retry decorator for inter-service communication.
    Logs service name for better debugging.
    
    Usage:
        @retry_service_call("syncvalue", max_attempts=5)
        async def get_ltv_prediction(user_id: str):
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{SYNCVALUE_URL}/predict-ltv/{user_id}")
                return response.json()
    """
    def decorator(func):
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=2, min=1, max=30),
            retry=retry_if_exception_type((httpx.HTTPError, ConnectionError)),
            before_sleep=before_sleep_log(
                logging.getLogger(f"retry.{service_name}"),
                logging.WARNING
            ),
            after=after_log(
                logging.getLogger(f"retry.{service_name}"),
                logging.INFO
            ),
            reraise=True
        )
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Sync versions for non-async code
def retry_sync(
    max_attempts: int = 3,
    backoff_multiplier: float = 1.0,
    max_delay: int = 10,
    exception_types: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Synchronous retry decorator.
    
    Usage:
        @retry_sync(max_attempts=5)
        def fetch_config():
            # ... synchronous operation
            pass
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=backoff_multiplier, min=1, max=max_delay),
        retry=retry_if_exception_type(exception_types),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO),
        reraise=True
    )
