from fastapi import APIRouter, Depends

from dependencies.user import get_users_service
from services.user import UsersService
from schemas.auth import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest, service: UsersService = Depends(get_users_service)
):
    """Аутентификация: выпуск JWT и создание сессии в Redis."""
    return await service.login(user=credentials)


# @router.get("/register_confirm")
# async def register_confirm(
#     token: str, service: UserService = Depends(get_users_service)
# ):
#     """Подтверждение email по токену из письма."""
#     await service.confirm_user(token=token)
#     return {"message": "Электронная почта подтверждена"}


# @router.get("/logout")
# async def logout(
#     current_user: UserMeResponse = Depends(get_current_user),
#     service: UserService = Depends(get_users_service),
# ):
#     """Выход: инвалидация сессии из токена."""
#     return await service.logout_user(user=current_user)
