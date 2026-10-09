import uuid

from fastapi import APIRouter, Depends, status, Query
from fastapi.exceptions import HTTPException

from dependencies.user import get_users_service
from services.user import UsersService, UserAlreadyExistsError, UserNotFoundError
from schemas.user import (
    UserCreateRequest,
    UserResponse,
    UserPaginatedResponse,
    UserUpdateRequest,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=UserPaginatedResponse)
async def get_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    users_service: UsersService = Depends(get_users_service),
):
    items, total = await users_service.get_list(page, per_page, search)
    return UserPaginatedResponse(
        total=total,
        page=page,
        per_page=per_page,
        users=items,
    )


@router.get("/{id}", response_model=UserResponse)
async def get_user(
    id: uuid.UUID, users_service: UsersService = Depends(get_users_service)
):
    try:
        return await users_service.get_by_id(id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/", response_model=UserResponse)
async def create_user(
    data: UserCreateRequest,
    users_service: UsersService = Depends(get_users_service),
):
    try:
        return await users_service.create(data)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.patch("/{id}", response_model=UserResponse)
async def update_user(
    id: uuid.UUID,
    data: UserUpdateRequest,
    users_service: UsersService = Depends(get_users_service),
):
    try:
        return await users_service.update(user_id=id, data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{id}", response_model=None)
async def delete_user(
    id: uuid.UUID, users_service: UsersService = Depends(get_users_service)
):
    try:
        return await users_service.delete(id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
