from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from config.dependency import Dependency
from .service import AuthenticationService
from .schemas import (
                        UserCreateBase, UserViewBase, UserUpdateBase, UserChangePasswordBase,
                        TokenAccessRefreshBase, TokenAccessBase)
from .models import UserModel


router_authentication = APIRouter()
dependency = Dependency()


@cbv(router_authentication)
class APIAuthenticationClass:

    db: AsyncSession = Depends(get_db)


    @router_authentication.post(path="/register/", status_code=status.HTTP_201_CREATED, response_model=UserViewBase)
    async def register_user(
                            self,
                            data: UserCreateBase):
        service = AuthenticationService(db=self.db)
        return await service.authentication_register_user(data=data)


    @router_authentication.post(path="/login/", status_code=status.HTTP_200_OK, response_model=TokenAccessRefreshBase)
    async def login(
                            self,
                            data: OAuth2PasswordRequestForm = Depends()):
        service = AuthenticationService(db=self.db)
        return await service.authentication_login(data=data)


    @router_authentication.post(path="/refresh/", status_code=status.HTTP_200_OK, response_model=TokenAccessBase)
    async def refresh(
                            self,
                            cuser: UserModel = Depends(dependency.refresh_token_dependency)):
        service = AuthenticationService(db=self.db, cuser=cuser)
        return await service.authentication_refresh()


    @router_authentication.put(path="/change_password/", status_code=status.HTTP_200_OK)
    async def change_password(
                            self,
                            data: UserChangePasswordBase,
                            cuser: UserModel = Depends(dependency.log_dependency)):
        service = AuthenticationService(db=self.db, cuser=cuser)
        return await service.authentication_change_password(data=data)


    @router_authentication.put(path="/update/", status_code=status.HTTP_200_OK, response_model=UserViewBase)
    async def update_user(
                            self,
                            data: UserUpdateBase,
                            cuser: UserModel = Depends(dependency.log_dependency)):
        service = AuthenticationService(db=self.db, cuser=cuser)
        return await service.authentication_update_user(data=data)


    @router_authentication.delete(path="/delete/", status_code=status.HTTP_200_OK)
    async def delete_user(
                            self,
                            cuser: UserModel = Depends(dependency.log_dependency)):
        service = AuthenticationService(db=self.db, cuser=cuser)
        return await service.authentication_delete_user()
