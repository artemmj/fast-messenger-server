import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from models.chat import ChatType


# === CHAT ===


class ChatCreate(BaseModel):
    type: ChatType = ChatType.GROUP
    name: Optional[str] = Field(None)


class UserMinResponse(BaseModel):
    id: uuid.UUID
    phone: str
    email: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ChatMemberResponse(BaseModel):
    user_id: uuid.UUID
    joined_at: datetime
    is_admin: bool
    user: UserMinResponse

    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    id: uuid.UUID
    type: ChatType = ChatType.GROUP
    name: Optional[str] = Field(None)
    created_at: datetime
    members: list[ChatMemberResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ChatPaginatedResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: list[ChatResponse]


# === CHAT_MEMBERSHIP ===


class ChatMembershipCreate(BaseModel):
    user_id: uuid.UUID
    chat_id: uuid.UUID


class ChatMembershipResponse(BaseModel):
    id: uuid.UUID
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatMembershipPaginatedResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: list[ChatMembershipResponse]


# === CHAT_MESSAGE ===


class ChatMessageCreate(BaseModel):
    text: str


class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatMessagePaginatedResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: list[ChatMessageResponse]
