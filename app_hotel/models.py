from sqlalchemy import Integer, String, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from config.database import Base
from datetime import date


class BookingModel(Base):
    __tablename__ = "booking"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    date_from: Mapped[date] = mapped_column(Date, nullable=False)
    date_to: Mapped[date] = mapped_column(Date, nullable=False)
    user: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    room: Mapped[int] = mapped_column(Integer, ForeignKey("room.id"), nullable=False)

    users = relationship("UserModel", back_populates="bookings")
    rooms = relationship("RoomModel", back_populates="bookings", lazy="selectin")


class RoomTypeModel(Base):
    __tablename__ = "roomtype"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    rooms = relationship("RoomModel", back_populates="roomtypes")


class RoomModel(Base):
    __tablename__ = "room"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    number: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    person: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Active")
    type: Mapped[int] = mapped_column(Integer, ForeignKey("roomtype.id"), nullable=False)

    bookings = relationship("BookingModel", back_populates="rooms", lazy="selectin")
    roomtypes = relationship("RoomTypeModel", back_populates="rooms", lazy="selectin")
