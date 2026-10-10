from typing import List, Optional
from sqlalchemy import select, exists
from sqlalchemy.orm import selectinload

from dependencies.db import DBDependency
from dao.base import BaseDAO
from models.chat import ChatMessage, ChatMembership
from schemas.chat import ChatMessageCreate


class ChatMessageDAO(BaseDAO[ChatMessage]):
    model = ChatMessage

    def __init__(self, db: DBDependency):
        super().__init__(db)

    async def is_user_in_chat(self, user_id: int, chat_id: int) -> bool:
        """
        Проверить, является ли пользователь участником чата.
        Используется для валидации прав перед отправкой сообщения.
        """
        async with self.db.read_only_scope() as session:
            stmt = select(
                exists().where(
                    (ChatMembership.user_id == user_id)
                    & (ChatMembership.chat_id == chat_id)
                )
            )
            result = await session.execute(stmt)
            return bool(result.scalar())

    async def create_message(
        self, sender_id: int, chat_id: int, message_data: ChatMessageCreate
    ) -> ChatMessage:
        """Создать и сохранить новое сообщение в чате"""
        async with self.db.transaction_scope() as session:
            new_message = self.model(
                chat_id=chat_id, sender_id=sender_id, text=message_data.text
            )
            session.add(new_message)
            await session.flush()
            await session.refresh(new_message)
            return new_message

    async def get_chat_history(
        self, chat_id: int, limit: int = 50, offset: int = 0
    ) -> List[ChatMessage]:
        """
        Получить историю сообщений конкретного чата с пагинацией.
        Загружает данные автора сообщения (User) через selectinload.
        Сортировка по времени: от старых к новым.
        """
        async with self.db.read_only_scope() as session:
            stmt = (
                select(self.model)
                .options(
                    selectinload(self.model.sender)
                )  # Подгружаем профиль отправителя
                .where(self.model.chat_id == chat_id)
                .order_by(
                    self.model.created_at.asc()
                )  # Для чатов обычно asc, для ленты новостей desc
                .limit(limit)
                .offset(offset)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_message_with_sender(self, message_id: int) -> Optional[ChatMessage]:
        """Получить одно конкретное сообщение вместе с данными отправителя"""
        async with self.db.read_only_scope() as session:
            stmt = (
                select(self.model)
                .options(selectinload(self.model.sender))
                .where(self.model.id == message_id)
            )
            result = await session.execute(stmt)
            return result.scalars().first()
