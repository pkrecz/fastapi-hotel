import logging
import asyncio
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from asgi_lifespan import LifespanManager
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer
from config.database import Base, get_db
from config.settings import settings
from main import app


stay_days = 1
ahead_days = 10


@pytest.fixture(scope="session")
async def async_engine():

    container = PostgresContainer("postgres:17.0-bookworm", driver="asyncpg")
    container.start()

    engine = create_async_engine(url=container.get_connection_url())

    async with engine.begin() as _engine:
        await _engine.run_sync(Base.metadata.drop_all)
        await _engine.run_sync(Base.metadata.create_all)
    logging.info("Configuration -----> Tables for testing has been created.")

    yield engine

    async with engine.begin() as _engine:
        await _engine.run_sync(Base.metadata.drop_all)
    logging.info("Configuration -----> Tables for testing has been removed.")

    container.stop()


@pytest.fixture(scope="session")
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:

    connection = await async_engine.connect()
    logging.info("Configuration -----> Connection established.")
    transaction = await connection.begin()
    logging.info("Configuration -----> Transaction started.")
    session = async_sessionmaker(
                                    autocommit=False,
                                    autoflush=False,
                                    expire_on_commit=False,
                                    bind=async_engine)()
    logging.info("Configuration -----> Session ready for running.")
    yield session
    await session.close()
    logging.info("Configuration -----> Session closed.")
    await transaction.rollback()
    logging.info("Configuration -----> Rollback executed.")
    await connection.close()
    logging.info("Configuration -----> Connection closed.")


@pytest_asyncio.fixture(scope="session")
async def async_client(event_loop, async_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:

    def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db
    logging.info("Configuration -----> Dependency overrided.")

    async with LifespanManager(app):
        async with AsyncClient(
                        transport=ASGITransport(app=app),
                        base_url="http://testserver") as client:
            logging.info("Configuration -----> Client ready for running.")
            yield client
            logging.info("Configuration -----> Client finished job.")


@pytest_asyncio.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


########################################## Authentication ###########################################
@pytest.fixture()
def data_test_register_user():
    return {
            "username": "test",
            "full_name": "User Test",
            "email": "test@example.com",
            "password": "!ws@test_password",
            "password_confirm": "!ws@test_password"}


@pytest.fixture()
def data_test_login():
    return {
            "username": "test",
            "password": "!ws@test_password"}


@pytest.fixture()
def data_test_update_user():
    return {
            "full_name": "User Test - update",
            "email": "test_update@example.com"}


@pytest.fixture()
def data_test_change_password():
    return {
            "old_password": "!ws@test_password",
            "new_password": "new@test_password",
            "new_password_confirm": "new@test_password"}


########################################## Hotel ###########################################
@pytest.fixture()
def data_test_create_room_type():
    return {
            "type": "Premium"}


@pytest.fixture()
def data_test_create_room():
    return {
            "number": "103A",
            "person": 3,
            "description": "Very good room."}


@pytest.fixture()
def data_test_update_room():
    return {
            "person": 1,
            "status": "Inactive"}


@pytest.fixture()
def data_test_create_booking():
    start_date = datetime.now().date() + timedelta(days=ahead_days)
    end_date = start_date + timedelta(days=stay_days)
    return {
            "date_from": str(start_date),
            "date_to": str(end_date)}


@pytest.fixture()
def data_test_result_get_free_room():
    return [
                {
                    "date_from": str(datetime.now().date()),
                    "date_to": str(datetime.now().date() + timedelta(days=ahead_days))},
                {
                    "date_from": str(datetime.now().date() + timedelta(days=ahead_days+stay_days)),
                    "date_to": str(datetime.now().date() + timedelta(days=int(settings.FUTURE_PERIOD_IN_DAYS)))}]
