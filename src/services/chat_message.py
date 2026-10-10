from typing import List
from dao.chat_message import ChatMessageDAO
from dependencies.db import db_dependency
from schemas.chat import ChatMessageResponse, ChatMessageCreate
from exceptions.chat import ChatAccessDeniedError


class ChatMessagesService:
    def __init__(self, message_dao: ChatMessageDAO):
        self.message_dao = message_dao

    async def send_message(
        self, sender_id: int, chat_id: int, data: ChatMessageCreate
    ) -> ChatMessageResponse:
        """Отправка сообщения в чат с предварительной проверкой доступа"""
        # Проверяем, состоит ли отправитель в этом чате
        is_allowed = await self.message_dao.is_user_in_chat(
            user_id=sender_id, chat_id=chat_id
        )
        if not is_allowed:
            raise ChatAccessDeniedError("У вас нет доступа к этому чату")

        message = await self.message_dao.create_message(
            sender_id=sender_id, chat_id=chat_id, message_data=data
        )

        # Подгружаем связанные данные (например, профиль sender), если необходимо для ответа
        full_message = await self.message_dao.get_message_with_sender(message.id)
        msg_dict = self.message_dao._model_to_dict(full_message or message)
        return ChatMessageResponse(**msg_dict)

    async def get_history(
        self, user_id: int, chat_id: int, limit: int = 50, offset: int = 0
    ) -> List[ChatMessageResponse]:
        """Получение истории сообщений чата с проверкой прав пользователя"""
        is_allowed = await self.message_dao.is_user_in_chat(
            user_id=user_id, chat_id=chat_id
        )
        if not is_allowed:
            raise ChatAccessDeniedError("У вас нет доступа к истории этого чата")

        messages = await self.message_dao.get_chat_history(
            chat_id=chat_id, limit=limit, offset=offset
        )
        return [
            ChatMessageResponse(**self.message_dao._model_to_dict(m)) for m in messages
        ]


def get_chat_messages_service() -> ChatMessagesService:
    """Фабрика сервиса сообщений"""
    return ChatMessagesService(message_dao=ChatMessageDAO(db_dependency))
