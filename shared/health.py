"""
Enhanced health check utilities for KIKI Agent services
Provides comprehensive dependency checking and metrics
"""

from typing import Dict, List, Optional, Callable, Any
from pydantic import BaseModel
from enum import Enum
import asyncio
import time
import httpx
from datetime import datetime


class HealthStatus(str, Enum):
    """Health check status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class DependencyHealth(BaseModel):
    """Individual dependency health status"""
    name: str
    status: HealthStatus
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    last_check: str


class ServiceHealth(BaseModel):
    """Overall service health response"""
    service: str
    status: HealthStatus
    version: str
    uptime_seconds: float
    timestamp: str
    dependencies: List[DependencyHealth]
    metrics: Dict[str, Any] = {}


class HealthChecker:
    """Enhanced health checker with dependency validation"""
    
    def __init__(self, service_name: str, version: str = "1.0.0"):
        self.service_name = service_name
        self.version = version
        self.start_time = time.time()
        self.dependency_checks: Dict[str, Callable] = {}
    
    def register_dependency(self, name: str, check_func: Callable):
        """Register a dependency health check function"""
        self.dependency_checks[name] = check_func
    
    async def check_http_endpoint(self, name: str, url: str, timeout: float = 2.0) -> DependencyHealth:
        """Check HTTP endpoint health"""
        start = time.time()
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                response_time = (time.time() - start) * 1000
                
                if response.status_code == 200:
                    return DependencyHealth(
                        name=name,
                        status=HealthStatus.HEALTHY,
                        response_time_ms=round(response_time, 2),
                        last_check=datetime.utcnow().isoformat() + "Z"
                    )
                else:
                    return DependencyHealth(
                        name=name,
                        status=HealthStatus.DEGRADED,
                        response_time_ms=round(response_time, 2),
                        error=f"HTTP {response.status_code}",
                        last_check=datetime.utcnow().isoformat() + "Z"
                    )
        except Exception as e:
            response_time = (time.time() - start) * 1000
            return DependencyHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=round(response_time, 2),
                error=str(e),
                last_check=datetime.utcnow().isoformat() + "Z"
            )
    
    async def check_database(self, name: str, db_connection) -> DependencyHealth:
        """Check database connection health"""
        start = time.time()
        try:
            # Simple query to verify connection
            if hasattr(db_connection, 'execute'):
                await db_connection.execute("SELECT 1")
            elif hasattr(db_connection, 'ping'):
                await db_connection.ping()
            else:
                # Fallback for sync connections
                pass
            
            response_time = (time.time() - start) * 1000
            return DependencyHealth(
                name=name,
                status=HealthStatus.HEALTHY,
                response_time_ms=round(response_time, 2),
                last_check=datetime.utcnow().isoformat() + "Z"
            )
        except Exception as e:
            response_time = (time.time() - start) * 1000
            return DependencyHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=round(response_time, 2),
                error=str(e),
                last_check=datetime.utcnow().isoformat() + "Z"
            )
    
    async def check_redis(self, name: str, redis_client) -> DependencyHealth:
        """Check Redis connection health"""
        start = time.time()
        try:
            await redis_client.ping()
            response_time = (time.time() - start) * 1000
            return DependencyHealth(
                name=name,
                status=HealthStatus.HEALTHY,
                response_time_ms=round(response_time, 2),
                last_check=datetime.utcnow().isoformat() + "Z"
            )
        except Exception as e:
            response_time = (time.time() - start) * 1000
            return DependencyHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=round(response_time, 2),
                error=str(e),
                last_check=datetime.utcnow().isoformat() + "Z"
            )
    
    async def get_health(self, metrics: Optional[Dict[str, Any]] = None) -> ServiceHealth:
        """Get comprehensive service health status"""
        # Check all registered dependencies
        dependency_results = []
        for dep_name, check_func in self.dependency_checks.items():
            try:
                result = await check_func()
                dependency_results.append(result)
            except Exception as e:
                dependency_results.append(
                    DependencyHealth(
                        name=dep_name,
                        status=HealthStatus.UNHEALTHY,
                        error=str(e),
                        last_check=datetime.utcnow().isoformat() + "Z"
                    )
                )
        
        # Determine overall status
        if all(dep.status == HealthStatus.HEALTHY for dep in dependency_results):
            overall_status = HealthStatus.HEALTHY
        elif any(dep.status == HealthStatus.UNHEALTHY for dep in dependency_results):
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        return ServiceHealth(
            service=self.service_name,
            status=overall_status,
            version=self.version,
            uptime_seconds=round(time.time() - self.start_time, 2),
            timestamp=datetime.utcnow().isoformat() + "Z",
            dependencies=dependency_results,
            metrics=metrics or {}
        )
