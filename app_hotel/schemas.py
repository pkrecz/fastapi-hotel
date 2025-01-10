from pydantic import BaseModel, model_validator, Field
from typing import Optional
from datetime import date, datetime
from . import exceptions


class RoomTypeCreateBase(BaseModel):
    type: str = Field(max_length=100, pattern="^[a-zA-Z0-9]*$")


class RoomTypeViewBase(BaseModel):
    id: int
    type: str


class RoomCreateBase(BaseModel):
    number: str = Field(max_length=10, pattern="^[a-zA-Z0-9]*$")
    person: int = Field(gt=0)
    type: int
    description: Optional[str] = Field(max_length=250)


class RoomUpdateBase(BaseModel):
    person: Optional[int] = Field(gt=0, default=None)
    type: Optional[int] = Field(default=None)
    description: Optional[str] = Field(max_length=250, default=None)
    status: Optional[str] = Field(max_length=50, default=None)


class BookingCreateBase(BaseModel):
    date_from: date
    date_to: date
    room: int

    @model_validator(mode="after")
    def check_range_of_dates(self):
        if self.date_from >= self.date_to or self.date_from < datetime.now().date():
            raise exceptions.IncorrectRangeDatesException
        return self


class BookingListBase(BaseModel):
    id: int
    date_from: date
    date_to: date
    status: str


class BookingFreeBase(BaseModel):
    date_from: date
    date_to: date


class RoomViewBase(BaseModel):
    id: int
    number: str
    person: int
    status: str
    description: Optional[str]
    bookings: Optional[list[BookingListBase]]
    roomtypes: RoomTypeViewBase


class RoomListBase(BaseModel):
    id: int
    number: str
    person: int
    description: Optional[str]
    roomtypes: RoomTypeViewBase


class RoomFreeBase(BaseModel):
    id: int
    person: int
    description: Optional[str]
    roomtypes: RoomTypeViewBase
    free_booking: list[BookingFreeBase]


class BookingViewBase(BaseModel):
    id: int
    date_from: date
    date_to: date
    status: str
    rooms: RoomListBase
