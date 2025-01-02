from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_restful.cbv import cbv
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from config.dependency import Dependency
from app_admin.models import UserModel
from .schemas import (
                        RoomTypeCreateBase, RoomTypeViewBase,
                        RoomCreateBase, RoomUpdateBase, RoomViewBase,
                        BookingCreateBase, BookingViewBase)
from .filters import RoomFilter
from .service import RoomTypeService, RoomService, BookingService


router_hotel = APIRouter()
dependency = Dependency()


@cbv(router_hotel)
class APIClass:

    db: AsyncSession = Depends(get_db)
    cuser: UserModel = Depends(dependency.log_dependency)

    @router_hotel.post(path="/roomtype/", response_model=RoomTypeViewBase, status_code=status.HTTP_201_CREATED)
    async def create_roomtype(
                                self,
                                data: RoomTypeCreateBase):
        service = RoomTypeService(db=self.db)
        return await service.roomtype_create(data=data)


    @router_hotel.delete(path="/roomtype/{id}/")
    async def delete_roomtype(
                                self,
                                id: int):
        service = RoomTypeService(db=self.db)
        await service.roomtype_delete(id=id)
        return JSONResponse(content={"message": "Room type deleted successfully."}, status_code=status.HTTP_200_OK)


    @router_hotel.post(path="/room/", response_model=RoomViewBase, status_code=status.HTTP_201_CREATED)
    async def create_room(
                                self,
                                data: RoomCreateBase):
        service = RoomService(db=self.db)
        return await service.room_create(data=data)


    @router_hotel.put(path="/room/{id}/", response_model=RoomViewBase, status_code=status.HTTP_200_OK)
    async def update_room(
                                self,
                                id: int,
                                data: RoomUpdateBase):
        service = RoomService(db=self.db)
        return await service.room_update(id=id, data=data)


    @router_hotel.delete(path="/room/{id}/")
    async def delete_room(
                                self,
                                id: int):
        service = RoomService(db=self.db)
        await service.room_delete(id=id)
        return JSONResponse(content={"message": "Room deleted successfully."}, status_code=status.HTTP_200_OK)


    @router_hotel.get(path="/room/", response_model=list[RoomViewBase], status_code=status.HTTP_200_OK)
    async def list_room(
						        self,
							    filter: RoomFilter = FilterDepends(RoomFilter)):
        service = RoomService(db=self.db)
        return await service.room_get_list(filter=filter)


    @router_hotel.post(path="/booking/", response_model=BookingViewBase, status_code=status.HTTP_201_CREATED)
    async def create_booking(
                                self,
                                data: BookingCreateBase):
        service = BookingService(db=self.db, cuser=self.cuser)
        return await service.booking_create(data=data)


    @router_hotel.get(path="/booking/", response_model=list[BookingViewBase], status_code=status.HTTP_200_OK)
    async def list_booking(self):
        service = BookingService(db=self.db, cuser=self.cuser)
        return await service.booking_list(self.cuser.id)