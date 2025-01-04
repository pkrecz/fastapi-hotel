from fastapi import HTTPException, status


class RoomTypeExistsException(HTTPException):
    def __init__(self):
        super().__init__(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Room type already exists.")


class RoomTypeNotExistsException(HTTPException):
    def __init__(self):
        super().__init__(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Room type does not exists.")


class RoomNumberExistsException(HTTPException):
    def __init__(self):
        super().__init__(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Room number already exists.")


class RoomNotExistsException(HTTPException):
    def __init__(self):
        super().__init__(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Room does not exists.")


class RoomNotAvailableException(HTTPException):
    def __init__(self):
        super().__init__(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Room is not available in this period of time.")


class BookingNotExistsException(HTTPException):
    def __init__(self):
        super().__init__(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Booking does not exists.")


class IncorrectRangeDatesException(HTTPException):
    def __init__(self):
        super().__init__(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Incorrect range of dates.")
