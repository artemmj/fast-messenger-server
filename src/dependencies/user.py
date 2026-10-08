from dao.user import UserDAO
from services.user import UsersService
from dependencies.db import db_dependency


def get_users_service() -> UsersService:
    """Фабрика сервиса."""
    return UsersService(user_dao=UserDAO(db_dependency))
