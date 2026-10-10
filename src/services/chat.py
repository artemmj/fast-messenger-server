from uuid import UUID
from typing import List

from dao.chat import ChatDAO
from dao.chat_membership import ChatMembershipDAO
from dependencies.db import db_dependency
from schemas.chat import ChatResponse, ChatCreate, ChatType
from exceptions.chat import ChatNotFoundError, ChatAccessDeniedError


class ChatService:
    """
    Сервис оркестрирует работу между ChatDAO и MembershipDAO для атомарного управления комнатами.
    """

    def __init__(self, chat_dao: ChatDAO, membership_dao: ChatMembershipDAO):
        self.chat_dao = chat_dao
        self.membership_dao = membership_dao

    async def create_group_chat(
        self, data: ChatCreate, creator_id: UUID
    ) -> ChatResponse:
        """Создание группового чата и автоматическое добавление создателя."""
        chat = await self.chat_dao.create_group_chat(data)
        await self.membership_dao.add_user_to_chat(user_id=creator_id, chat_id=chat.id)
        chat_dict = self.chat_dao._model_to_dict(chat)
        return ChatResponse(**chat_dict)

    async def create_personal_chat(
        self, user1_id: UUID, user2_id: UUID
    ) -> ChatResponse:
        """Создание личного чата между двумя пользователями"""
        if user1_id == user2_id:
            raise ValueError("Нельзя создать личный чат с самим собой")

        existing = await self.chat_dao.get_personal_chat_between_users(
            user1_id, user2_id
        )
        if existing:
            chat_dict = self.chat_dao._model_to_dict(existing)
            return ChatResponse(**chat_dict)

        chat = await self.chat_dao.create_personal_chat(user1_id, user2_id)
        chat_dict = self.chat_dao._model_to_dict(chat)
        return ChatResponse(**chat_dict)

    async def get_user_chats(self, user_id: UUID) -> List[ChatResponse]:
        """Получение всех чатов конкретного пользователя"""
        chats = await self.chat_dao.get_user_chats(user_id)
        return [ChatResponse(**self.chat_dao._model_to_dict(c)) for c in chats]

    async def add_member(
        self, chat_id: UUID, user_id: UUID, current_user_id: UUID
    ) -> None:
        """Добавление нового пользователя в групповой чат"""
        chat = await self.chat_dao.get_by_id(chat_id)
        if not chat:
            raise ChatNotFoundError(f"Chat {chat_id} not found")
        if chat.type == ChatType.PERSONAL:
            raise ValueError("Нельзя добавлять участников в личный чат")

        # Проверяем, имеет ли право текущий пользователь приглашать (состоит ли он сам там)
        if not await self.membership_dao.is_member(
            user_id=current_user_id, chat_id=chat_id
        ):
            raise ChatAccessDeniedError("Вы не являетесь участником этого чата")

        await self.membership_dao.add_user_to_chat(user_id=user_id, chat_id=chat_id)

    async def leave_chat(self, chat_id: UUID, user_id: UUID) -> None:
        """Выход пользователя из чата"""
        chat = await self.chat_dao.get_by_id(chat_id)
        if not chat:
            raise ChatNotFoundError(f"Chat {chat_id} not found")

        deleted = await self.membership_dao.remove_user_from_chat(
            user_id=user_id, chat_id=chat_id
        )
        if not deleted:
            raise ChatAccessDeniedError("Вы не состоите в этом чате")


def get_chats_service() -> ChatService:
    """Фабрика сервиса чатов"""
    return ChatService(
        chat_dao=ChatDAO(db_dependency), membership_dao=ChatMembershipDAO(db_dependency)
    )
