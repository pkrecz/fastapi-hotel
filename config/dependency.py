from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar
from config.database import Base, get_db
from app_admin import exceptions
from app_admin.models import UserModel
from app_admin.repository import AuthenticationRepository


Model = TypeVar("Model", bound=Base)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login/")


class Dependency:

    async def log_dependency(
                                        self,
                                        token: str = Depends(oauth2_scheme),
                                        db: AsyncSession = Depends(get_db)) -> Model:
        self.auth = AuthenticationRepository(db, UserModel)
        username = self.auth.verify_token(token=token, refresh=False)
        if username is None:
            raise exceptions.CredentialsException
        instance = await self.auth.get_user_by_username(username)
        if await self.auth.get_active_status(instance.username) == False:
            raise exceptions.UserInActiveException
        return instance


    async def refresh_token_dependency(
                                        self,
                                        token: str = Depends(oauth2_scheme),
                                        db: AsyncSession = Depends(get_db)) -> Model:
        self.auth = AuthenticationRepository(db, UserModel)
        username = self.auth.verify_token(token=token, refresh=True)
        if username is None:
            raise exceptions.CredentialsException
        instance = await self.auth.get_user_by_username(username=username)
        if await self.auth.get_active_status(instance.username) == False:
            raise exceptions.UserInActiveException
        return instance
