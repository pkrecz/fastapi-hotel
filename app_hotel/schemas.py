from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date


class RoomTypeCreateBase(BaseModel):
    type: str


class RoomTypeViewBase(BaseModel):
    id: int
    type: str


class RoomCreateBase(BaseModel):
    number: str
    person: int
    type: int
    description: Optional[str]


class RoomUpdateBase(BaseModel):
    person: Optional[int] = None
    type: Optional[int] = None
    description: Optional[str] = None
    status: Optional[str] = None


class RoomViewBase(BaseModel):
    id: int
    number: str
    person: int
    status: str
    description: Optional[str]
    booking: Optional[int]
    roomtypes: RoomTypeViewBase


class BookingCreateBase(BaseModel):
    date_from: date
    date_to: date


class BookingViewBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_from: date
    date_to: date
