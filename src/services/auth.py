from fastapi import status, HTTPException

from dao.user import UserDAO
from schemas.auth import LoginRequest, LoginResponse


class AuthService:
    def __init__(self, user_dao: UserDAO):
        self.user_dao = user_dao

    async def login(self, user: LoginRequest) -> LoginResponse:
        exist_user = await self.user_dao.get_by_email(email=user.email)
        if exist_user is None or not await self.auth_handler.verify_password(
            user.password, exist_user["password_hash"]
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Wrong email or password",
            )
        if not exist_user["is_active"] or exist_user["is_banned"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled or banned",
            )
        token, session_id = await self.auth_handler.create_access_token(
            user_id=exist_user["id"]
        )
        await self._store_access_token(
            token=token, user_id=exist_user["id"], session_id=session_id
        )
        return LoginResponse(access_token=token)
