from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from services.chat import ChatService, get_chats_service
from exceptions.chat import (
    ChatNotFoundError,
    ChatAccessDeniedError,
    GroupChatNeedNameError,
    ChatLimitExceededError,
)
from schemas.chat import ChatResponse, ChatCreate
from schemas.user import UserResponse
from dependencies.auth import get_current_user

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.post("/group", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_group_chat(
    data: ChatCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: ChatService = Depends(get_chats_service),
):
    """Создать новый групповой чат (текущий пользователь добавляется автоматически)"""
    try:
        return await service.create_group_chat(data, creator_id=current_user.id)
    except GroupChatNeedNameError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ChatLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/personal/{companion_id}", response_model=ChatResponse)
async def create_personal_chat(
    companion_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ChatService = Depends(get_chats_service),
):
    """Создать личный чат (тет-а-тет) с другим пользователем"""
    try:
        return await service.create_personal_chat(
            user1_id=current_user.id, user2_id=companion_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=List[ChatResponse])
async def get_my_chats(
    current_user: UserResponse = Depends(get_current_user),
    service: ChatService = Depends(get_chats_service),
):
    """Получить список всех чатов, в которых состоит текущий пользователь"""
    return await service.get_user_chats(user_id=current_user.id)


@router.post("/{chat_id}/members/{user_id}", status_code=status.HTTP_200_OK)
async def add_member_to_chat(
    chat_id: UUID,
    user_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ChatService = Depends(get_chats_service),
):
    """Добавить пользователя в групповой чат (доступно только участникам этого чата)"""
    try:
        await service.add_member(
            chat_id=chat_id, user_id=user_id, current_user_id=current_user.id
        )
        return {"status": "success", "detail": "User added to chat"}
    except ChatNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ChatAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{chat_id}/members/leave", status_code=status.HTTP_200_OK)
async def leave_chat(
    chat_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ChatService = Depends(get_chats_service),
):
    """Самостоятельно покинуть чат"""
    try:
        await service.leave_chat(chat_id=chat_id, user_id=current_user.id)
        return {"status": "success", "detail": "You left the chat"}
    except ChatNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ChatAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
