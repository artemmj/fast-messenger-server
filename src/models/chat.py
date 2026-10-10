import enum
from uuid import UUID
from datetime import datetime

from sqlalchemy import Boolean, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.user import User
from models.mixins import FullMixin


class ChatType(str, enum.Enum):
    PERSONAL = "personal"
    GROUP = "group"


class Chat(Base, FullMixin):
    type: Mapped[ChatType] = mapped_column(
        String(16),
        default=ChatType.GROUP,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(127), nullable=True)

    members: Mapped[list["ChatMembership"]] = relationship(
        back_populates="chat", cascade="all, delete-orphan"
    )
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="chat", cascade="all, delete-orphan"
    )


class ChatMessage(Base, FullMixin):
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chat.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(String(255), nullable=False)
    is_read: Mapped[Boolean] = mapped_column(Boolean, nullable=False, default=False)

    chat: Mapped["Chat"] = relationship(back_populates="messages")
    sender: Mapped["User"] = relationship(back_populates="messages")


class ChatMembership(Base, FullMixin):
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chat.id", ondelete="CASCADE"))
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="memberships")
    chat: Mapped["Chat"] = relationship(back_populates="members")
