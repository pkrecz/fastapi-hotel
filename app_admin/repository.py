import bcrypt
from fastapi.security import OAuth2PasswordBearer
from functools import lru_cache
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from typing import TypeVar
from datetime import datetime, timedelta, timezone
from config.settings import settings
from config.database import Base
from . import exceptions


Model = TypeVar("Model", bound=Base)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login/")


class AuthenticationRepository:

    def __init__(self, db: AsyncSession = None, model: Model = None):
        self.db = db
        self.model = model


    async def check_if_exists_user_by_id(self, id: int) -> bool:
        query = select(self.model).filter(self.model.id == id)
        query = exists(query).select()
        return await self.db.scalar(query)


    async def check_if_exists_user_by_username(self, username: str) -> bool:
        query = select(self.model).filter(self.model.username == username)
        query = exists(query).select()
        return await self.db.scalar(query)


    async def check_if_exists_user_by_email(self, email: str) -> bool:
        query = select(self.model).filter(self.model.email == email)
        query = exists(query).select()
        return await self.db.scalar(query)


    @lru_cache
    async def get_user_by_id(self, id: int) -> Model:
        return await self.db.get(self.model, id)


    @lru_cache
    async def get_user_by_username(self, username: str) -> Model:
        query = select(self.model).filter(self.model.username == username)
        return await self.db.scalar(query)


    @lru_cache
    async def get_active_status(self, username: str) -> bool:
        query = select(self.model).filter(self.model.username == username)
        instance = await self.db.scalar(query)
        return bool(instance.is_active)


    async def authenticate_user(self, username: str, password: str) -> Model:
        instance = await self.get_user_by_username(username=username)
        if instance and self.verify_password(password, instance.hashed_password) == True:
            return instance
        else:
            return False


    def check_the_same_password(self, password: str, password_confirm: str) -> bool:
        return bool(password == password_confirm)


    def hash_password(self, password: str) -> str:
        pwd = password.encode("utf-8")
        salt = bcrypt.gensalt()
        return str(bcrypt.hashpw(password=pwd, salt=salt).decode("utf-8"))


    def verify_password(self, password: str, hashed_password: str) -> bool:
        pwd = password.encode("utf-8")
        hashed_pwd = hashed_password.encode("utf-8")
        return bool(bcrypt.checkpw(password=pwd, hashed_password=hashed_pwd))


    def create_token(self, data: dict, refresh: bool) -> str:
        to_encode = data.copy()
        if refresh:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
            secret_key = settings.REFRESH_SECRET_KEY
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            secret_key = settings.ACCESS_SECRET_KEY
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)
        return str(encoded_jwt)


    def verify_token(self, token: str, refresh: bool) -> str:
        try:
            if refresh:
                payload = jwt.decode(token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
            else:
                payload = jwt.decode(token, settings.ACCESS_SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except jwt.ExpiredSignatureError:
            raise exceptions.TokenExpiredException
        except JWTError:
            return None
