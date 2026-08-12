from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class SignUpSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=6)

class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: str
    createdAt: Optional[datetime]
    updatedAt: Optional[datetime]

class LoginResponse(BaseModel):
    token: str
    user: UserResponse