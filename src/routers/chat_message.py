from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List

from exceptions.chat import ChatAccessDeniedError
from services.chat_message import ChatMessagesService, get_chat_messages_service
from schemas.chat import ChatMessageResponse, ChatMessageCreate
from schemas.user import UserResponse
from dependencies.auth import get_current_user
from dao.chat_membership import ChatMembershipDAO
from dependencies.db import db_dependency
from services.websocket import ws_manager

router = APIRouter(prefix="/chats", tags=["Messages"])


@router.post(
    "/{chat_id}/send_message",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    chat_id: UUID,
    data: ChatMessageCreate,
    current_user: UserResponse = Depends(get_current_user),
    message_service: ChatMessagesService = Depends(get_chat_messages_service),
):
    """Отправить сообщение в указанный чат"""
    saved_message = await message_service.send_message(
        user_id=current_user.id, chat_id=chat_id, data=data
    )

    try:
        membership_dao = ChatMembershipDAO(db_dependency)
        member_ids = await membership_dao.get_chat_member_ids(chat_id=chat_id)

        message_payload = {
            "event": "new_message",
            "chat_id": chat_id,
            "data": saved_message.model_dump(mode="json"),
        }

        signal_payload = {
            "event": "chat_signal",
            "chat_id": chat_id,
            "data": {
                "last_message_text": data.text[:50],
                "last_message_time": saved_message.created_at.isoformat(),
                "sender_id": str(current_user.id),
            },
        }

        await ws_manager.broadcast_to_chat(
            message=message_payload, member_ids=member_ids
        )
        await ws_manager.broadcast_to_chat(
            message=signal_payload, member_ids=member_ids
        )

    except ChatAccessDeniedError as e:
        print(f"🚨 Ошибка реалтайм-рассылки через HTTP-роут: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # 3. Возвращаем стандартный ответ инициатору HTTP-запроса
    return saved_message


@router.get("/{chat_id}/get_messages", response_model=List[ChatMessageResponse])
async def get_chat_history(
    chat_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserResponse = Depends(get_current_user),
    service: ChatMessagesService = Depends(get_chat_messages_service),
):
    """Получить историю сообщений чата с поддержкой пагинации"""
    try:
        return await service.get_history(
            user_id=current_user.id, chat_id=chat_id, limit=limit, offset=offset
        )
    except ChatAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
