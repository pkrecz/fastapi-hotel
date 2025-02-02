from fastapi import BackgroundTasks
from fastapi_filter.contrib.sqlalchemy import Filter
from functools import lru_cache
from typing import TypeVar
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import Base
from config.settings import settings
from util.crudrepository import CrudOperationRepository
from util.filesupport import convert_xlsx_to_list_of_dict
from .models import RoomTypeModel, RoomModel, BookingModel
from .repository import RoomTypeRepository, RoomRepository, BookingRepository
from .schemas import RoomCreateBase
from . import exceptions


Model = TypeVar("Model", bound=Base)


class RoomTypeService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = RoomTypeModel
        self.crud = CrudOperationRepository(self.db, self.model)
        self.roomtype = RoomTypeRepository(self.db, self.model)


    async def roomtype_create(self, data: BaseModel) -> Model:
        if await self.roomtype.check_if_exists_room_type_by_type(data.type):
            raise exceptions.RoomTypeExistsException
        return await self.crud.create(data)


    async def roomtype_delete(self, id: int) -> bool:
        if not await self.roomtype.check_if_exists_room_type_by_id(id):
            raise exceptions.RoomTypeNotExistsException
        return await self.crud.delete(id)


class RoomService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = RoomModel
        self.crud = CrudOperationRepository(self.db, self.model)
        self.room = RoomRepository(self.db, self.model)
        self.room_type = RoomTypeRepository(self.db, RoomTypeModel)


    async def room_create(self, data: BaseModel) -> Model:
        if await self.room.check_if_exists_room_by_number(data.number):
            raise exceptions.RoomNumberExistsException
        return await self.crud.create(data)


    async def room_create_import(self, data: BaseModel) -> bool:
        list_of_rooms = await convert_xlsx_to_list_of_dict(file=data.file)
        list_of_room_type = await self.room_type.get_all_room_type()

        @lru_cache
        def get_id_by_room_type(list_of_room_types: list = list_of_room_type, room_type: str = None) -> int:
            for single_type in list_of_room_types:
                if single_type.type == room_type:
                    return single_type.id

        try:
            for single_room in list_of_rooms:
                room_type_id = get_id_by_room_type(room_type=single_room["type"])
                single_room.update({"type": room_type_id})
                RoomCreateBase(**single_room)
            return await self.crud.create_all(list_of_rooms)
        except:
            raise exceptions.InconsistencyDataException


    async def room_update(self, id: int, data: BaseModel) -> Model:
        if not await self.room.check_if_exists_room_by_id(id):
            raise exceptions.RoomNotExistsException
        return await self.crud.update(id, data)


    async def room_delete(self, id: int) -> bool:
        if not await self.room.check_if_exists_room_by_id(id):
            raise exceptions.RoomNotExistsException
        return await self.crud.delete(id)


    async def room_get_list(self, filter: Filter = None) -> Model:
        instance = await self.crud.get_all(filter)
        return await self.crud.list(instance)


    @lru_cache
    async def room_free_get_list(self) -> Model:
        instance = await self.room.get_free_room(int(settings.FUTURE_PERIOD_IN_DAYS))
        return await self.crud.list(instance)


class BookingService:

    def __init__(self, db: AsyncSession, cuser: Model = None, background_task: BackgroundTasks = None):
        self.db = db
        self.cuser = cuser
        self.background_task = background_task
        self.crud = CrudOperationRepository(self.db, BookingModel)
        self.booking = BookingRepository(self.db, BookingModel)


    async def booking_create(self, data: BaseModel) -> Model:
        input = {**data.model_dump(), "user": self.cuser.id}
        if not await self.booking.check_availability_room(
                                                            id=data.room,
                                                            date_from=data.date_from,
                                                            date_to=data.date_to):
            raise exceptions.RoomNotAvailableException
        instance = await self.crud.create(input)
        await self.booking.create_confirmation_send_email(
                                                            id=instance.id,
                                                            background_task=self.background_task)
        return instance


    async def booking_delete(self, id) -> bool:
        if not await self.booking.check_if_exists_booking_by_id(id):
            raise exceptions.BookingNotExistsException
        return await self.crud.delete(id)


    async def booking_list(self, filter: Filter = None) -> Model:
        instance = await self.crud.get_all(filter)
        return await self.crud.list(instance)


    async def booking_check_in(self, id: int):
        if not await self.booking.check_if_exists_booking_by_id(id):
            raise exceptions.BookingNotExistsException
        data = {"status": "CheckIn"}
        return await self.crud.update(id, data)


    async def booking_check_out(self, id: int):
        if not await self.booking.check_if_exists_booking_by_id(id):
            raise exceptions.BookingNotExistsException
        data = {"status": "CheckOut"}
        return await self.crud.update(id, data)
