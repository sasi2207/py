# schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    # Accepts 'full_name', 'fullName', or 'name' (or defaults to empty string if missing)
    full_name: Optional[str] = Field(default="", alias="fullName")
    role: Optional[str] = "student"

    class Config:
        populate_by_name = True  # Allows both 'full_name' and 'fullName'

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse