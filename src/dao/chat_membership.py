from typing import List
from sqlalchemy import select, delete, exists

from dependencies.db import DBDependency
from dao.base import BaseDAO
from models.chat import ChatMembership, User


class ChatMembershipDAO(BaseDAO[ChatMembership]):
    model = ChatMembership

    def __init__(self, db: DBDependency):
        super().__init__(db)

    async def add_user_to_chat(self, user_id: int, chat_id: int) -> ChatMembership:
        """Добавить пользователя в чат (вступить или пригласить)"""
        async with self.db.transaction_scope() as session:
            # Проверяем, не состоит ли пользователь уже в чате, чтобы не плодить дубликаты
            stmt = select(self.model).where(
                (self.model.user_id == user_id) & (self.model.chat_id == chat_id)
            )
            result = await session.execute(stmt)
            existing_member = result.scalars().first()

            if existing_member:
                return existing_member

            # Если не состоит, создаем новую запись
            new_member = self.model(user_id=user_id, chat_id=chat_id)
            session.add(new_member)
            await session.flush()
            await session.refresh(new_member)
            return new_member

    async def remove_user_from_chat(self, user_id: int, chat_id: int) -> bool:
        """Удалить пользователя из чата (выйти из чата / кикнуть)"""
        async with self.db.transaction_scope() as session:
            stmt = delete(self.model).where(
                (self.model.user_id == user_id) & (self.model.chat_id == chat_id)
            )
            result = await session.execute(stmt)
            # Если rowcount > 0, значит запись успешно удалена
            return result.rowcount > 0

    async def get_chat_members_profiles(self, chat_id: int) -> List[User]:
        """Получить список профилей (User) всех участников конкретного чата"""
        async with self.db.read_only_scope() as session:
            stmt = (
                select(User)
                .join(self.model, self.model.user_id == User.id)
                .where(self.model.chat_id == chat_id)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def is_member(self, user_id: int, chat_id: int) -> bool:
        """Быстрая проверка: является ли пользователь участником чата"""
        async with self.db.read_only_scope() as session:
            stmt = select(
                exists().where(
                    (self.model.user_id == user_id) & (self.model.chat_id == chat_id)
                )
            )
            result = await session.execute(stmt)
            return bool(result.scalar())
