import uuid
import datetime
from typing import Annotated, Optional  # , List

from pydantic import BaseModel, Field, StringConstraints


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    phone: Optional[str] = None

    is_active: bool
    is_banned: bool
    is_superuser: bool
    is_verified: bool

    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class UserPaginatedResponse(BaseModel):
    total: int
    page: int
    per_page: int
    users: list[UserResponse]


class UserCreateRequest(BaseModel):
    email: str = Field(..., min_length=5, example="john@example.com")
    phone: Optional[str] = Field(None, min_length=5, example="+79112223344")

    password: Annotated[str, StringConstraints(min_length=3, max_length=32)]


class UserUpdateRequest(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None

    is_active: Optional[bool] = None
    is_banned: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None
