from typing import TypeVar
from pydantic import BaseModel
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import Base
from util.crudrepository import CrudOperationRepository
from . import exceptions
from .repository import AuthenticationRepository
from .models import UserModel


Model = TypeVar("Model", bound=Base)


class AuthenticationService:

    def __init__(self, db: AsyncSession, cuser: str = None):
        self.db = db
        self.cuser = cuser
        self.model = UserModel
        self.auth = AuthenticationRepository(self.db, UserModel)
        self.crud = CrudOperationRepository(self.db, UserModel)


    async def authentication_register_user(self, data: BaseModel) -> Model:
        if await self.auth.check_if_exists_user_by_username(data.username):
            raise exceptions.UserExistsException
        if await self.auth.check_if_exists_user_by_email(data.email):
            raise exceptions.EmailExistsException
        if self.auth.check_the_same_password(data.password, data.password_confirm) == False:
            raise exceptions.NotTheSamePasswordException
        input = {
                    **data.model_dump(exclude={"password", "password_confirm"}),
                    "hashed_password": self.auth.hash_password(data.password)}
        return await self.crud.create(input)


    async def authentication_update_user(self, id: int, data: BaseModel) -> Model:
        if not await self.auth.check_if_exists_user_by_id(id): 
            raise exceptions.UserNotFoundException
        return await self.crud.update(id, data)


    async def authentication_delete_user(self, id: int):
        if not await self.auth.check_if_exists_user_by_id(id):
            raise exceptions.UserNotFoundException
        if not await self.crud.delete(id):
            raise
        return JSONResponse(content={"message": "User deleted successfully."}, status_code=status.HTTP_200_OK)


    async def authentication_change_password(self, id: int, data: BaseModel):
        instance = await self.auth.get_user_by_id(id)
        if not instance:
            raise exceptions.UserNotFoundException
        if self.auth.check_the_same_password(data.new_password, data.new_password_confirm) == False:
            raise exceptions.NotTheSamePasswordException
        if self.auth.verify_password(data.old_password, instance.hashed_password) == False:
            raise exceptions.IncorrectPasswordException
        data = {"hashed_password": self.auth.hash_password(data.new_password)}
        await self.crud.update(id, data)
        return JSONResponse(content={"message": "Password changed successfully."}, status_code=status.HTTP_200_OK)


    async def authentication_login(self, data: OAuth2PasswordBearer):
        instance = await self.auth.authenticate_user(data.username, data.password)
        if not instance:
            raise exceptions.CredentialsException
        if await self.auth.get_active_status(instance.username) == False:
            raise exceptions.UserInActiveException
        access_token = self.auth.create_token(data={"sub": instance.username}, refresh=False)
        refresh_token = self.auth.create_token(data={"sub": instance.username}, refresh=True)
        return JSONResponse(content={"access_token": access_token, "refresh_token": refresh_token}, status_code=status.HTTP_200_OK)


    async def authentication_refresh(self):
        access_token = self.auth.create_token(data={"sub": self.cuser.username}, refresh=False)
        return JSONResponse(content={"access_token": access_token}, status_code=status.HTTP_200_OK)
