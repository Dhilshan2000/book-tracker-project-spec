from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the book")
    author: str = Field(..., min_length=1, description="Author of the book")
    genre: Optional[str] = Field(default=None, description="Genre of the book")
    year: Optional[int] = Field(default=None, ge=0, le=3000, description="Publication year")
    is_read: bool = Field(default=False, description="Whether the book has been read")

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    author: Optional[str] = Field(default=None, min_length=1)
    genre: Optional[str] = None
    year: Optional[int] = Field(default=None, ge=0, le=3000)
    is_read: Optional[bool] = None

class BookResponse(BookBase):
    id: str = Field(..., description="Unique identifier for the book")
    user_id: str = Field(..., description="Firebase UID of the user who owns this book")

    model_config = ConfigDict(from_attributes=True)

