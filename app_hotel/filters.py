from typing import Optional
from fastapi_filter.contrib.sqlalchemy import Filter
from .models import RoomModel


class RoomFilter(Filter):
    status: Optional[str] = None
    person: Optional[int] = None
    order_by: Optional[list[str]] = None

    class Constants(Filter.Constants):
        model = RoomModel
