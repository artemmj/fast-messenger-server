from typing import Optional, Tuple, List, Dict  # , Any

from sqlalchemy import select, exists, func, or_

from dao.base import BaseDAO
from models.user import User

from dependencies.db import DBDependency


class UserDAO(BaseDAO[User]):
    model = User

    def __init__(self, db: DBDependency):
        super().__init__(db)

    async def check_uniques(self, email: str, phone: str | None) -> bool:
        async with self.db.read_only_scope() as session:
            stmt = select(exists().where(or_(self.model.email == email)))
            if phone:
                stmt = stmt._or(self.model.phone == phone)
            result = await session.execute(stmt)
            return result.scalar()

    async def check_uniques_excluding_user(
        self, email: str, phone: str | None, exclude_user_id: int
    ) -> bool:
        async with self.db.read_only_scope() as session:
            conditions = [self.model.email == email]
            if phone is not None and phone.strip():
                conditions.append(self.model.phone == phone)
            stmt = select(
                exists().where(
                    self.model.id != exclude_user_id,
                    or_(*conditions)
                )
            )
            result = await session.execute(stmt)
            return result.scalar()

    # async def get_by_id(self, id: int) -> Optional[Dict[str, Any]]:
    #     async with self.db.read_only_scope() as session:
    #         result = await session.execute(
    #             select(self.model).where(self.model.id == id)
    #         )
    #         obj = result.scalar_one_or_none()
    #         if obj:
    #             return self._model_to_dict(obj)
    #         return None

    async def get_paginated_list(
        self, page: int, per_page: int, search: Optional[str] = None
    ) -> Tuple[List[Dict], int]:
        async with self.db.read_only_scope() as session:
            query = select(self.model)
            count_query = select(func.count(self.model.id))

            if search:
                pattern = f"%{search}%"
                filter_cond = or_(
                    self.model.email.ilike(pattern),
                    self.model.phone.ilike(pattern),
                )
                query = query.where(filter_cond)
                count_query = count_query.where(filter_cond)

            total = (await session.execute(count_query)).scalar_one()

            result = await session.execute(
                query.order_by(self.model.created_at)
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
            users = result.scalars().unique().all()

            items = [
                {
                    "id": user.id,
                    "email": user.email,
                    "phone": user.phone,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                    "is_active": user.is_active,
                    "is_superuser": user.is_superuser,
                    "is_banned": user.is_banned,
                    "is_verified": user.is_verified,
                }
                for user in users
            ]

            return items, total
