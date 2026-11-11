from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User email address")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")

class UserResponse(UserBase):
    id: str = Field(..., description="Firebase UID of the user")

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str = Field(..., description="Firebase ID token")
    token_type: str = "bearer"

