from sqlalchemy import Integer, String, Boolean, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from config.database import Base


class UserModel(Base):
    __tablename__ = "user"
    __table_args__ = (
                        Index("idx_user_id", "id", postgresql_using="btree"),
                        Index("idx_user_username", "username", postgresql_using="btree"))

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(250), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    bookings = relationship("BookingModel", back_populates="users")
