from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User email address")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")

class UserResponse(UserBase):
    id: str = Field(..., description="Unique identifier for the user")
    created_at: Optional[datetime] = Field(default=None, description="Account creation timestamp")

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    email: Optional[str] = None
    exp: Optional[int] = None

