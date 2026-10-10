import uuid
from typing import List, Optional
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from dependencies.db import DBDependency
from dao.base import BaseDAO
from models.chat import Chat, ChatMembership, ChatType
from schemas.chat import ChatCreate


class ChatDAO(BaseDAO[Chat]):
    model = Chat

    def __init__(self, db: DBDependency):
        super().__init__(db)

    async def create_group_chat(self, data: ChatCreate) -> Chat:
        async with self.db.session_scope() as session:
            new_chat = self.model(type=ChatType.GROUP, name=data.name)
            session.add(new_chat)
            await session.flush()
            await session.refresh(new_chat)
            return new_chat

    async def get_personal_chat_between_users(
        self, user1_id: uuid.UUID, user2_id: uuid.UUID
    ) -> Optional[Chat]:
        """
        Проверить, существует ли уже личный чат между двумя пользователями.
        Использует read_only_scope для безопасного чтения. Идемпотентный.
        """
        async with self.db.read_only_scope() as session:
            stmt = (
                select(self.model)
                .join(ChatMembership)
                .where(
                    and_(
                        self.model.type == ChatType.PERSONAL,
                        ChatMembership.user_id.in_([user1_id, user2_id]),
                    )
                )
                .group_by(self.model.id)
                # Если оба user_id входят, то записей в группе должно быть 2
                .having(func.count(ChatMembership.id) == 2)
            )
            result = await session.execute(stmt)
            return result.scalars().first()

    async def create_personal_chat(
        self, user1_id: uuid.UUID, user2_id: uuid.UUID
    ) -> Chat:
        """
        Создать личный чат между двумя пользователями.
        Если чат уже существует, возвращает его без создания нового.
        """
        # 1. Сначала проверяем существование через read_only_scope внутри метода
        existing_chat = await self.get_personal_chat_between_users(user1_id, user2_id)
        if existing_chat:
            return existing_chat

        # 2. Если чата нет, открываем транзакцию на запись
        async with self.db.transaction_scope() as session:
            new_chat = self.model(type=ChatType.PERSONAL, name=None)
            session.add(new_chat)
            await session.flush()  # Генерируем id для new_chat.id

            # Добавляем связи для обоих участников
            member1 = ChatMembership(user_id=user1_id, chat_id=new_chat.id)
            member2 = ChatMembership(user_id=user2_id, chat_id=new_chat.id)
            session.add_all([member1, member2])

            await session.flush()
            await session.refresh(new_chat)
            return new_chat

    async def get_chat_with_members(self, chat_id: uuid.UUID) -> Optional[Chat]:
        """Получить чат по ID вместе со всеми его участниками (жадная загрузка)"""
        async with self.db.read_only_scope() as session:
            stmt = (
                select(self.model)
                .options(
                    selectinload(self.model.members).selectinload(ChatMembership.user)
                )
                .where(self.model.id == chat_id)
            )
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_user_chats(self, user_id: uuid.UUID) -> List[Chat]:
        """Получить список всех чатов, в которых состоит конкретный пользователь"""
        async with self.db.read_only_scope() as session:
            stmt = (
                select(self.model)
                .join(ChatMembership)
                .where(ChatMembership.user_id == user_id)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
