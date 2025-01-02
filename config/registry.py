import logging
from fastapi.middleware.cors import CORSMiddleware
from config.database import Base, get_engine
from app_admin import controlers as admin_controlers
from app_hotel import controlers as hotel_controlers


logger = logging.getLogger("uvicorn.error")


async def init_models():
    async with get_engine().begin() as transaction:
        await transaction.run_sync(Base.metadata.create_all)
    logger.info("Tables has been created.")


def init_routers(app):
    app.include_router(
                        router=admin_controlers.router_authentication,
                        prefix="/admin",
                        tags=["Authentication"])
    app.include_router(
                        router=hotel_controlers.router_hotel,
                        prefix="",
                        tags=["Hotel - booking"])
    logger.info("Routers has been loaded.")


def init_middleware(app):
    app.add_middleware(
                        CORSMiddleware,
                        allow_origins=["*"],
                        allow_credentials=True,
                        allow_methods=["*"],
                        allow_headers=["*"])
    logger.info("Middleware has been added.")
