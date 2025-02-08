import os
from sqlalchemy.exc import DatabaseError, SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from collections.abc import AsyncGenerator
from dotenv import load_dotenv
from .util import Singleton
from .redis import get_redis_sync


load_dotenv()

class Base(DeclarativeBase):
    pass


redis_session = next(get_redis_sync())
url = os.getenv("DATABASE_URL", default=os.getenv("DATABASE_URL_LOCAL"))


def get_engine(db_url: str = url):
    cached_value = redis_session.get("db_url")
    if cached_value is not None:
        url = cached_value
    else:
        redis_session.set("db_url", db_url, ex=3600)
        url = db_url
    return create_async_engine(url=url, pool_pre_ping=True)


def get_session():
    session = async_sessionmaker(
                                    autocommit=False,
                                    autoflush=False,
                                    expire_on_commit=False,
                                    bind=get_engine())
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
