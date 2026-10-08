from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from models import Base, FullMixin


class User(Base, FullMixin):
    email: Mapped[str] = mapped_column(String(127), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(15), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # roles: Mapped[list[Role]] = relationship(
    #     secondary="user_roles",
    #     back_populates="users",
    #     lazy="selectin",
    # )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, email={self.email})"
