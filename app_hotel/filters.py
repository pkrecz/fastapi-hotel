from typing import Optional
from datetime import date
from fastapi_filter.contrib.sqlalchemy import Filter
from .models import RoomModel, BookingModel


class RoomFilter(Filter):
    status: Optional[str] = None
    person: Optional[int] = None
    order_by: Optional[list[str]] = None

    class Constants(Filter.Constants):
        model = RoomModel


class BookingFilter(Filter):
    id: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    status: Optional[str] = None
    order_by: Optional[list[str]] = None

    class Constants(Filter.Constants):
        model = BookingModel
