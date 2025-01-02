from typing import TypeVar
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_filter.contrib.sqlalchemy import Filter
from config.database import Base
from .models import RoomTypeModel, RoomModel, BookingModel
from .repository import CrudOperationRepository, BookingRepository


Model = TypeVar("Model", bound=Base)


class RoomTypeService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = RoomTypeModel
        self.crud = CrudOperationRepository(self.db, self.model)


    async def roomtype_create(self, data: BaseModel) -> Model:
        return await self.crud.create(data)


    async def roomtype_delete(self, id) -> bool:
        return await self.crud.delete(id)


class RoomService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = RoomModel
        self.crud = CrudOperationRepository(self.db, self.model)


    async def room_create(self, data: BaseModel) -> Model:
        return await self.crud.create(data)


    async def room_update(self, id: int, data: BaseModel) -> Model:
        return await self.crud.update(id, data)


    async def room_delete(self, id) -> bool:
        return await self.crud.delete(id)


    async def room_get_list(self, filter: Filter = None) -> Model:
        instance = await self.crud.get_all(filter)
        return await self.crud.list(instance)


class BookingService:

    def __init__(self, db: AsyncSession, cuser: Model):
        self.db = db
        self.cuser = cuser
        self.model = BookingModel
        self.crud = CrudOperationRepository(self.db, self.model)
        self.hotel = BookingRepository(self.db, self.model)


    async def booking_create(self, data: BaseModel) -> Model:
        input = {**data.model_dump(), "owner": self.cuser.id}
        return await self.crud.create(input)


    async def booking_list(self, user_id: int) -> Model:
        instance = await self.hotel.get_booking_by_user(user_id)
        return await self.crud.list(instance)
