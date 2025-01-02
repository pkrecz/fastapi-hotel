import os
from sqlalchemy.exc import DatabaseError, SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from collections.abc import AsyncGenerator
from functools import cache
from dotenv import load_dotenv
from .util import Singleton


class Base(DeclarativeBase):
    pass


load_dotenv()
url = os.getenv("DATABASE_URL")


@cache
def get_engine(db_url: str = url):
    return create_async_engine(db_url)


def get_session():
    session = async_sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return session()


class DatabaseSessionClass(metaclass=Singleton):

    async def __aenter__(self):
        self.db = get_session()
        return self.db

    async def __aexit__(self, exc_type, exc_value: str, exc_traceback: str) -> None:
        try:
            if any([exc_type, exc_value, exc_traceback]):
                raise
            await self.db.commit()
        except (SQLAlchemyError, DatabaseError, Exception) as exception:
            await self.db.rollback()
            raise exception
        finally:
            await self.db.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with DatabaseSessionClass() as db:
        yield db
