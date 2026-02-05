"""
Enhanced input validation utilities for KIKI Agent services
Quick Win #9: Implements Pydantic validators and sanitization
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Any, List
import re
from datetime import datetime
import bleach

class EnhancedValidation:
    """
    Collection of reusable validation methods.
    Can be used in Pydantic models or standalone.
    """
    
    @staticmethod
    def sanitize_html(value: str) -> str:
        """Remove potentially dangerous HTML/scripts"""
        if not value:
            return value
        return bleach.clean(value, tags=[], strip=True)
    
    @staticmethod
    def validate_email(value: str) -> str:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValueError("Invalid email format")
        return value.lower()
    
    @staticmethod
    def validate_user_id(value: str) -> str:
        """Validate user ID format (alphanumeric + underscore/hyphen)"""
        if not re.match(r'^[a-zA-Z0-9_-]{3,64}$', value):
            raise ValueError("Invalid user ID format (3-64 alphanumeric characters)")
        return value
    
    @staticmethod
    def validate_url(value: str) -> str:
        """Validate URL format"""
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, value, re.IGNORECASE):
            raise ValueError("Invalid URL format")
        return value
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize and truncate string input"""
        if not value:
            return value
        # Remove control characters
        value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
        # Truncate to max length
        return value[:max_length].strip()
    
    @staticmethod
    def validate_phone(value: str) -> str:
        """Validate phone number (international format)"""
        # Remove common formatting characters
        cleaned = re.sub(r'[\s\-\(\)\.]', '', value)
        if not re.match(r'^\+?[1-9]\d{1,14}$', cleaned):
            raise ValueError("Invalid phone number format")
        return cleaned
    
    @staticmethod
    def validate_positive_number(value: float) -> float:
        """Ensure number is positive"""
        if value <= 0:
            raise ValueError("Value must be positive")
        return value
    
    @staticmethod
    def validate_percentage(value: float) -> float:
        """Validate percentage (0-100)"""
        if not 0 <= value <= 100:
            raise ValueError("Percentage must be between 0 and 100")
        return value
    
    @staticmethod
    def validate_future_date(value: datetime) -> datetime:
        """Ensure date is in the future"""
        if value <= datetime.utcnow():
            raise ValueError("Date must be in the future")
        return value


# Example models with enhanced validation

class UserInput(BaseModel):
    """Example: User input with validation"""
    user_id: str = Field(..., min_length=3, max_length=64)
    email: str
    phone: Optional[str] = None
    bio: Optional[str] = None
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        return EnhancedValidation.validate_user_id(v)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return EnhancedValidation.validate_email(v)
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v:
            return EnhancedValidation.validate_phone(v)
        return v
    
    @field_validator('bio')
    @classmethod
    def sanitize_bio(cls, v):
        if v:
            return EnhancedValidation.sanitize_string(v, max_length=500)
        return v


class CampaignConfig(BaseModel):
    """Example: Campaign configuration with validation"""
    campaign_id: str
    budget: float = Field(..., gt=0, le=1000000)
    bid_multiplier: float = Field(default=1.0, ge=0.1, le=10.0)
    target_urls: List[str] = Field(default_factory=list, max_length=100)
    start_date: datetime
    end_date: datetime
    
    @field_validator('target_urls')
    @classmethod
    def validate_urls(cls, v):
        return [EnhancedValidation.validate_url(url) for url in v]
    
    @model_validator(mode='after')
    def validate_dates(self):
        """Ensure end_date is after start_date"""
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class LTVPredictionRequest(BaseModel):
    """Example: LTV prediction request with validation"""
    user_id: str
    features: dict = Field(..., min_length=1)
    ltv_threshold: Optional[float] = Field(None, ge=0, le=10000)
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        return EnhancedValidation.validate_user_id(v)
    
    @field_validator('features')
    @classmethod
    def validate_features(cls, v):
        """Ensure all feature values are numeric"""
        for key, value in v.items():
            if not isinstance(value, (int, float)):
                raise ValueError(f"Feature '{key}' must be numeric")
            if not -1e9 <= value <= 1e9:
                raise ValueError(f"Feature '{key}' value out of range")
        return v


class BidRequest(BaseModel):
    """Example: Real-time bid request with validation"""
    auction_id: str
    user_id: str
    bid_floor: float = Field(..., ge=0.01, le=100.0)
    timeout_ms: int = Field(default=100, ge=10, le=1000)
    
    @field_validator('auction_id')
    @classmethod
    def validate_auction_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9-]{10,50}$', v):
            raise ValueError("Invalid auction_id format")
        return v
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        return EnhancedValidation.validate_user_id(v)


# Size limit middleware for FastAPI
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to limit request body size.
    Prevents memory exhaustion from large payloads.
    """
    
    def __init__(self, app, max_size_mb: int = 10):
        super().__init__(app)
        self.max_size = max_size_mb * 1024 * 1024  # Convert to bytes
    
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_size:
            raise HTTPException(
                status_code=413,
                detail=f"Request body too large. Maximum size: {self.max_size // 1024 // 1024}MB"
            )
        return await call_next(request)
