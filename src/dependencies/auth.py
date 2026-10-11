import uuid
from typing import Annotated

from fastapi import WebSocket, HTTPException, Depends, Query
from starlette import status
from starlette.requests import Request

from services.auth import AuthService, get_auth_service
from services.user import UsersService, get_users_service
from handlers.auth import AuthHandler
from schemas.user import UserResponse
from exceptions.auth import WebSocketAuthError


async def get_token_from_headers(request: Request) -> str:
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing"
        )
    return token


async def get_current_user(
    token: Annotated[str, Depends(get_token_from_headers)],
    auth_handler: AuthHandler = Depends(AuthHandler),
    auth_service: AuthService = Depends(get_auth_service),
    users_service: UsersService = Depends(get_users_service),
) -> UserResponse:
    decoded_token = await auth_handler.decode_access_token(token=token)

    user_id = decoded_token.get("user_id")
    session_id = decoded_token.get("session_id")

    if not await auth_service.get_access_token(user_id=user_id, session_id=session_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid"
        )

    user = await users_service.get_by_id(user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        phone=user.phone,
        is_active=user.is_active,
        is_banned=user.is_banned,
        is_superuser=user.is_superuser,
        is_verified=user.is_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        session_id=session_id,
        # roles=user["roles"],
    )


async def get_ws_current_user(
    websocket: WebSocket, token: str = Query(..., description="JWT access token")
) -> uuid.UUID:
    """Валидация токена для WebSocket-соединения без вызова HTTP-ошибок"""
    auth_handler = AuthHandler()
    try:
        payload = await auth_handler.decode_access_token(token)
        user_id_str = payload.get("sub")

        if not user_id_str:
            print("🚨 WS Auth Error: В токене отсутствует поле 'sub'")
            await websocket.accept()
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise WebSocketAuthError()

        return uuid.UUID(user_id_str)
    except Exception:
        try:
            await websocket.accept()
        except Exception:
            pass
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketAuthError()
