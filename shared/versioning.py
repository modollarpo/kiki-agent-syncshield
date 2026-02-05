"""
API versioning utilities for KIKI Agent services
Quick Win #8: Implements /v1, /v2 API versioning
"""

from fastapi import FastAPI, APIRouter, Request, HTTPException
from typing import Callable, Optional, Dict
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class APIVersionRouter:
    """
    Manages multiple API versions with automatic routing.
    Supports /v1, /v2, etc. prefixes for backward compatibility.
    """
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.versions: Dict[str, APIRouter] = {}
        self.default_version: Optional[str] = None
    
    def create_version_router(
        self,
        version: str,
        prefix: str = None,
        tags: list = None,
        deprecated: bool = False
    ) -> APIRouter:
        """
        Create a new versioned router.
        
        Args:
            version: Version string (e.g., "v1", "v2")
            prefix: Optional prefix override (default: /{version})
            tags: OpenAPI tags for this version
            deprecated: Mark version as deprecated in OpenAPI
        
        Returns:
            APIRouter for this version
        
        Usage:
            versioning = APIVersionRouter(app)
            v1_router = versioning.create_version_router("v1")
            v2_router = versioning.create_version_router("v2")
            
            @v1_router.get("/users")
            def get_users_v1():
                return {"version": "v1", "users": [...]}
            
            @v2_router.get("/users")
            def get_users_v2():
                return {"version": "v2", "data": {"users": [...]}}
        """
        if version in self.versions:
            logger.warning(f"Version {version} already exists, returning existing router")
            return self.versions[version]
        
        router = APIRouter(
            prefix=prefix or f"/{version}",
            tags=tags or [version],
            deprecated=deprecated
        )
        
        self.versions[version] = router
        self.app.include_router(router)
        
        logger.info(f"Created API version router: {version} (deprecated={deprecated})")
        return router
    
    def set_default_version(self, version: str):
        """Set default API version (routes without version prefix use this)"""
        if version not in self.versions:
            raise ValueError(f"Version {version} does not exist")
        self.default_version = version
        logger.info(f"Set default API version to: {version}")
    
    def get_version_from_request(self, request: Request) -> str:
        """Extract API version from request path"""
        path_parts = request.url.path.split("/")
        if len(path_parts) > 1 and path_parts[1].startswith("v"):
            return path_parts[1]
        return self.default_version or "v1"


def version_header_required(supported_versions: list = ["v1", "v2"]):
    """
    Middleware to enforce API version via header.
    
    Usage:
        @app.middleware("http")
        @version_header_required(supported_versions=["v1", "v2"])
        async def version_middleware(request: Request, call_next):
            return await call_next(request)
    """
    def middleware(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, call_next):
            # Check for API version in header
            api_version = request.headers.get("X-API-Version") or request.headers.get("API-Version")
            
            if api_version:
                if api_version not in supported_versions:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unsupported API version: {api_version}. Supported: {supported_versions}"
                    )
                # Add version to request state for use in handlers
                request.state.api_version = api_version
            
            return await call_next(request)
        return wrapper
    return middleware


def deprecated_endpoint(
    deprecation_message: str,
    sunset_date: Optional[str] = None,
    alternative_endpoint: Optional[str] = None
):
    """
    Decorator to mark endpoints as deprecated with helpful messaging.
    
    Args:
        deprecation_message: Message explaining deprecation
        sunset_date: ISO date when endpoint will be removed (e.g., "2026-12-31")
        alternative_endpoint: Suggested alternative endpoint
    
    Usage:
        @app.get("/old-endpoint")
        @deprecated_endpoint(
            deprecation_message="Use /v2/new-endpoint instead",
            sunset_date="2026-06-01",
            alternative_endpoint="/v2/new-endpoint"
        )
        def old_endpoint():
            return {"data": "..."}
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Log deprecation warning
            logger.warning(
                f"Deprecated endpoint called: {func.__name__}. {deprecation_message}"
            )
            
            # Execute original function
            response = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # Add deprecation headers to response
            if hasattr(response, 'headers'):
                response.headers['Deprecation'] = 'true'
                if sunset_date:
                    response.headers['Sunset'] = sunset_date
                if alternative_endpoint:
                    response.headers['Link'] = f'<{alternative_endpoint}>; rel="successor-version"'
            
            return response
        return wrapper
    return decorator


import asyncio


def create_versioned_app(
    title: str,
    description: str,
    supported_versions: list = ["v1"],
    default_version: str = "v1"
) -> tuple[FastAPI, APIVersionRouter]:
    """
    Factory function to create FastAPI app with versioning built-in.
    
    Returns:
        Tuple of (FastAPI app, APIVersionRouter)
    
    Usage:
        app, versioning = create_versioned_app(
            title="My API",
            description="Versioned API",
            supported_versions=["v1", "v2"],
            default_version="v2"
        )
        
        v1 = versioning.create_version_router("v1", deprecated=True)
        v2 = versioning.create_version_router("v2")
    """
    app = FastAPI(
        title=title,
        description=f"{description} (Versions: {', '.join(supported_versions)})",
        version=default_version
    )
    
    versioning = APIVersionRouter(app)
    
    # Create routers for all supported versions
    for version in supported_versions:
        is_deprecated = version != default_version
        versioning.create_version_router(version, deprecated=is_deprecated)
    
    versioning.set_default_version(default_version)
    
    return app, versioning
