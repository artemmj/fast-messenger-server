from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query

from services.websocket import ws_manager
from services.chat_message import ChatMessagesService, get_chat_messages_service
from exceptions.chat import ChatAccessDeniedError
from dao.chat_membership import ChatMembershipDAO
from dependencies.db import db_dependency
from dependencies.auth import get_ws_current_user
from schemas.chat import ChatMessageCreate
from exceptions.auth import WebSocketAuthError

router = APIRouter(tags=["WebSockets"])


@router.websocket("/ws/chats")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    message_service: ChatMessagesService = Depends(get_chat_messages_service),
):
    """Устанавливает постоянное WebSocket-соединение для обмена сообщениями в реальном времени..."""
    try:
        user_id = await get_ws_current_user(websocket, token)
    except WebSocketAuthError:
        return

    await ws_manager.connect(str(user_id), websocket)

    membership_dao = ChatMembershipDAO(db_dependency)

    try:
        while True:
            data = await websocket.receive_json()

            chat_id = data.get("chat_id")
            text = data.get("text")

            if not chat_id or not text:
                continue

            try:
                str_chat_id = str(chat_id)

                message_in_db = ChatMessageCreate(text=text)
                saved_message = await message_service.send_message(
                    user_id=user_id, chat_id=str_chat_id, data=message_in_db
                )

                member_ids = await membership_dao.get_chat_member_ids(
                    chat_id=str_chat_id
                )

                message_payload = {
                    "event": "new_message",
                    "chat_id": str_chat_id,
                    "data": saved_message.model_dump(mode="json"),
                }
                signal_payload = {
                    "event": "chat_signal",
                    "chat_id": str_chat_id,
                    "data": {
                        "last_message_text": text[:50],
                        "last_message_time": saved_message.created_at.isoformat(),
                        "sender_id": str(user_id),
                    },
                }
                await ws_manager.broadcast_to_chat(
                    message=message_payload, member_ids=[str(_id) for _id in member_ids]
                )
                await ws_manager.broadcast_to_chat(
                    message=signal_payload, member_ids=[str(_id) for _id in member_ids]
                )
            except ChatAccessDeniedError as e:
                await websocket.send_json(
                    {
                        "event": "error",
                        "detail": "Вы не состоите в этом чате и не можете отправлять сообщения.",
                        "e": str(e),
                    }
                )
            except Exception as e:
                await websocket.send_json(
                    {
                        "event": "error",
                        "detail": "Произошла ошибка при обработке сообщения.",
                        "e": str(e),
                    }
                )
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id, websocket)
