"""User account models: what's stored, what's accepted on signup, what's returned."""
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from app.models.common import MongoBaseModel, PyObjectId, utcnow

Role = Literal["admin", "grower", "viewer"]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=120)
    role: Role = "grower"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserInDB(MongoBaseModel):
    email: EmailStr
    full_name: str
    role: Role = "grower"
    hashed_password: str
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: utcnow().isoformat())


class UserPublic(BaseModel):
    id: PyObjectId
    email: EmailStr
    full_name: str
    role: Role
    is_active: bool
