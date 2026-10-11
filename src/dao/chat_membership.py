from uuid import UUID
from typing import List
from sqlalchemy import select, delete, exists

from dependencies.db import DBDependency
from dao.base import BaseDAO
from models.chat import ChatMembership, User


class ChatMembershipDAO(BaseDAO[ChatMembership]):
    model = ChatMembership

    def __init__(self, db: DBDependency):
        super().__init__(db)

    async def add_user_to_chat(self, user_id: UUID, chat_id: UUID) -> ChatMembership:
        async with self.db.session_scope() as session:
            new_member = self.model(user_id=user_id, chat_id=chat_id)
            session.add(new_member)
            await session.flush()
            await session.refresh(new_member)
            return new_member

    async def remove_user_from_chat(self, user_id: UUID, chat_id: UUID) -> bool:
        """Удалить пользователя из чата (выйти из чата / кикнуть)"""
        async with self.db.session_scope() as session:
            stmt = delete(self.model).where(
                (self.model.user_id == user_id) & (self.model.chat_id == chat_id)
            )
            result = await session.execute(stmt)
            # Если rowcount > 0, значит запись успешно удалена
            return result.rowcount > 0

    async def get_chat_members_profiles(self, chat_id: UUID) -> List[User]:
        """Получить список профилей (User) всех участников конкретного чата"""
        async with self.db.read_only_scope() as session:
            stmt = (
                select(User)
                .join(self.model, self.model.user_id == User.id)
                .where(self.model.chat_id == chat_id)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def is_member(self, user_id: UUID, chat_id: UUID) -> bool:
        """Быстрая проверка: является ли пользователь участником чата"""
        async with self.db.read_only_scope() as session:
            stmt = select(
                exists().where(
                    (self.model.user_id == user_id) & (self.model.chat_id == chat_id)
                )
            )
            result = await session.execute(stmt)
            return bool(result.scalar())

    async def get_chat_member_ids(self, chat_id: UUID) -> List[UUID]:
        async with self.db.read_only_scope() as session:
            stmt = select(self.model.user_id).where(self.model.chat_id == chat_id)
            result = await session.execute(stmt)
            return list(result.scalars().all())
