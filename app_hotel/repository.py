from typing import TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, or_
from datetime import date, timedelta
from config.database import Base


Model = TypeVar("Model", bound=Base)


class RoomTypeRepository:

    def __init__(self, db: AsyncSession, model: Model):
        self.db = db
        self.model = model


    async def check_if_exists_room_type_by_type(self, type: str) -> bool:
        query = select(self.model).filter(self.model.type == type)
        query = exists(query).select()
        return await self.db.scalar(query)


    async def check_if_exists_room_type_by_id(self, id: int) -> bool:
        query = select(self.model).filter(self.model.id == id)
        query = exists(query).select()
        return await self.db.scalar(query)


class RoomRepository:

    def __init__(self, db: AsyncSession, model: Model):
        self.db = db
        self.model = model


    async def check_if_exists_room_by_number(self, number: str) -> bool:
        query = select(self.model).filter(self.model.number == number)
        query = exists(query).select()
        return await self.db.scalar(query)


    async def check_if_exists_room_by_id(self, id: int) -> bool:
        query = select(self.model).filter(self.model.id == id)
        query = exists(query).select()
        return await self.db.scalar(query)


class BookingRepository:

    def __init__(self, db: AsyncSession, model: Model):
        self.db = db
        self.model = model


    async def check_if_exists_booking_by_id(self, id: int) -> bool:
        query = select(self.model).filter(self.model.id == id)
        query = exists(query).select()
        return await self.db.scalar(query)


    def create_list_of_days(self, start_date: date, stop_date: date) -> list:
        date_list = list()
        while start_date <= stop_date:
            date_list.append(start_date)
            start_date += timedelta(days=1)
        return date_list


    async def create_occupied_days_list(self, id: int) -> list:
        occupied_days_list = list()
        filter_status_list = list()
        for condition in ["Active", "CheckIn"]:
            filter_status_list.append(self.model.status == condition)
        query = select(self.model).filter(self.model.room == id, or_(*filter_status_list))
        instance = await self.db.scalars(query)
        for item in instance.all():
            occupied_days_list += self.create_list_of_days(start_date=item.date_from, stop_date=item.date_to)
        occupied_days_list = list(set(occupied_days_list))
        occupied_days_list.sort()
        return occupied_days_list


    async def get_booking_by_user(self, id: int) -> Model:
        query = select(self.model).filter(self.model.user == id)
        instance = await self.db.scalars(query)
        return instance.all()


    async def check_availability_room(self, id: int, date_from: date, date_to: date) -> bool:
        requested_days_list = self.create_list_of_days(start_date=date_from, stop_date=date_to)
        occupied_days_list = await self.create_occupied_days_list(id=id)
        for day in requested_days_list[1::]:
            if day in occupied_days_list:
                return False
        return True
