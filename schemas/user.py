from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: str
    email: EmailStr
    name: str
    is_active: bool = True
