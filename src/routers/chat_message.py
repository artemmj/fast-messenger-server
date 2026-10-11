from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List

from exceptions.chat import ChatAccessDeniedError
from services.chat_message import ChatMessagesService, get_chat_messages_service
from schemas.chat import ChatMessageResponse, ChatMessageCreate
from schemas.user import UserResponse
from dependencies.auth import get_current_user

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
    service: ChatMessagesService = Depends(get_chat_messages_service),
):
    """Отправить сообщение в указанный чат"""
    try:
        return await service.send_message(
            user_id=current_user.id, chat_id=chat_id, data=data
        )
    except ChatAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


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
