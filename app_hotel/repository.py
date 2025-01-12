from typing import TypeVar
from fastapi import BackgroundTasks
from fastapi_mail import MessageSchema
from sqlalchemy import select, exists, or_, not_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager
from datetime import date, datetime, timedelta
from config.database import Base
from util.mailservice import send_email
from .models import BookingModel
from app_admin.models import UserModel


Model = TypeVar("Model", bound=Base)


def create_list_of_days(start_date: date, stop_date: date) -> list:
        date_list = list()
        while start_date <= stop_date:
            date_list.append(start_date)
            start_date += timedelta(days=1)
        return date_list


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


    async def calculate_difference_ahead_in_days(self, list_days: list, idx: int) -> int:
        return (list_days[idx + 1] - list_days[idx]).days


    async def transform_days_to_period(self, list_of_days: list) -> list:
        list_of_free_period = list()
        day_from_status = False
        day_to_status = False
        scope = len(list_of_days) - 1

        for idx in range(scope):

            if await self.calculate_difference_ahead_in_days(list_of_days, idx) == 1 and day_from_status == False:
                day_from = list_of_days[idx]
                if day_from > datetime.now().date():
                    day_from -= timedelta(days=1) 
                day_from_status = True

            if (await self.calculate_difference_ahead_in_days(list_of_days, idx) > 1 \
                                                                                and day_from_status == True) \
                                                                                or idx + 1 == scope:
                day_to = list_of_days[idx] + timedelta(days=1)
                day_to_status = True

            if day_from_status and day_to_status:
                list_of_free_period.append({"date_from": day_from, "date_to": day_to})
                day_from_status = False
                day_to_status = False

        return list_of_free_period


    async def create_list_of_free_period(self, occupied_booking: Model, future_period_in_days: int) -> list:
        list_of_free_period = list()
        list_of_occupied_days = list()
        list_of_free_days = list()
        counter_date = datetime.now().date()
        stop_date = counter_date + timedelta(days=future_period_in_days)

        for one_booking in occupied_booking:
            list_of_occupied_days += create_list_of_days(
                                                            start_date=one_booking.date_from,
                                                            stop_date=one_booking.date_to)
        list_of_occupied_days = list(set(list_of_occupied_days))
        list_of_occupied_days.sort()

        while counter_date <= stop_date:
            if counter_date not in list_of_occupied_days:
                list_of_free_days.append(counter_date)
            counter_date += timedelta(days=1)

        list_of_free_period = await self.transform_days_to_period(list_of_free_days)

        return list_of_free_period


    async def get_free_room(self, future_period_in_days: int) -> Model:
        query = select(self.model) \
                                    .join(self.model.bookings) \
                                    .filter(
                                                self.model.status == "Active",
                                                not_(BookingModel.status == "CheckOut")) \
                                    .options(
                                                contains_eager(self.model.bookings) \
                                                .load_only(BookingModel.date_from, BookingModel.date_to))
        instance = await self.db.scalars(query)
        instance = instance.unique().all()
        for item in instance:
            list_of_free_period = await self.create_list_of_free_period(
                                                                            occupied_booking=item.bookings,
                                                                            future_period_in_days=future_period_in_days)
            item.free_booking = list_of_free_period
        return instance


class BookingRepository:

    def __init__(self, db: AsyncSession, model: Model):
        self.db = db
        self.model = model


    async def check_if_exists_booking_by_id(self, id: int) -> bool:
        query = select(self.model).filter(self.model.id == id)
        query = exists(query).select()
        return await self.db.scalar(query)


    async def create_occupied_days_list(self, id: int) -> list:
        occupied_days_list = list()
        filter_status_list = list()
        for condition in ["Active", "CheckIn"]:
            filter_status_list.append(self.model.status == condition)
        query = select(self.model).filter(self.model.room == id, or_(*filter_status_list))
        instance = await self.db.scalars(query)
        for item in instance.all():
            occupied_days_list += create_list_of_days(start_date=item.date_from, stop_date=item.date_to)
        occupied_days_list = list(set(occupied_days_list))
        occupied_days_list.sort()
        return occupied_days_list


    async def get_booking_by_user(self, id: int) -> Model:
        query = select(self.model).filter(self.model.user == id)
        instance = await self.db.scalars(query)
        return instance.all()


    async def get_email_by_booking_id(self, id: int) -> str:
        query = select(UserModel.email) \
                                            .join(BookingModel, UserModel.bookings) \
                                            .filter(BookingModel.id == id)
        return await self.db.scalar(query)


    async def check_availability_room(self, id: int, date_from: date, date_to: date) -> bool:
        requested_days_list = create_list_of_days(start_date=date_from, stop_date=date_to)
        occupied_days_list = await self.create_occupied_days_list(id=id)
        for day in requested_days_list[1::]:
            if day in occupied_days_list:
                return False
        return True


    async def create_confirmation_send_email(self, id: int, background_task: BackgroundTasks):
        email = await self.get_email_by_booking_id(id=id)
        subject = "Confirmation of your booking"
        body = {
                "title": "Congratulations !!!",
                "context": f"We confirm your booking ID: {id}"}
        template_name = "confirmation_mail.html"

        message = MessageSchema(
                                subject=subject,
                                recipients=[email],
                                template_body=body,
                                subtype="html")
        await send_email(
                            message=message,
                            template_name=template_name,
                            background_task=background_task)
