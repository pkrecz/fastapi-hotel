from typing import TypeVar
from pydantic import BaseModel
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import Base
from . import exceptions
from .repository import AuthenticationRepository, CrudOperationRepository
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
            "username": data.username,
            "full_name": data.full_name,
            "email": data.email,
            "hashed_password": self.auth.hash_password(data.password)}
        return await self.crud.create(input)


    async def authentication_update_user(self, data: BaseModel) -> Model:
        instance = await self.auth.get_user_by_username(self.cuser.username)
        if not instance:
            raise exceptions.UserNotFoundException
        return await self.crud.update(instance, data)


    async def authentication_delete_user(self):
        instance = await self.auth.get_user_by_username(self.cuser.username)
        if not instance:
            raise exceptions.UserNotFoundException
        if not await self.crud.delete(instance):
            raise
        return JSONResponse(content={"message": "User deleted successfully."}, status_code=status.HTTP_200_OK)


    async def authentication_change_password(self, data: BaseModel):
        instance = await self.auth.get_user_by_username(self.cuser.username)
        if not instance:
            raise exceptions.UserNotFoundException
        if self.auth.check_the_same_password(data.new_password, data.new_password_confirm) == False:
            raise exceptions.NotTheSamePasswordException
        if self.auth.verify_password(data.old_password, instance.hashed_password) == False:
            raise exceptions.IncorrectPasswordException
        data = {"hashed_password": self.auth.hash_password(data.new_password)}
        await self.crud.update(instance, data)
        return JSONResponse(content={"message": "Password changed successfully."}, status_code=status.HTTP_200_OK)


    async def authentication_login(self, data: OAuth2PasswordBearer):
        user = await self.auth.authenticate_user(data.username, data.password)
        if not user:
            raise exceptions.CredentialsException
        if await self.auth.get_active_status(user.username) == False:
            raise exceptions.UserInActiveException
        access_token = self.auth.create_token(data={"sub": user.username}, refresh=False)
        refresh_token = self.auth.create_token(data={"sub": user.username}, refresh=True)
        return JSONResponse(content={"access_token": access_token, "refresh_token": refresh_token}, status_code=status.HTTP_200_OK)


    async def authentication_refresh(self):
        access_token = self.auth.create_token(data={"sub": self.cuser.username}, refresh=False)
        return JSONResponse(content={"access_token": access_token}, status_code=status.HTTP_200_OK)
