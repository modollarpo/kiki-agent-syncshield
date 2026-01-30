from pydantic import BaseModel
from typing import Optional

class Creative(BaseModel):
    creative_id: str
    prompt: str
    variant: str
    user_id: str
    image_url: Optional[str]
    brand_safety: Optional[str]
    ratings: Optional[list]
