from fastapi import FastAPI
from config.settings import settings
from config import registry
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await registry.init_models()
    registry.init_routers(app)
    yield


app = FastAPI(
                lifespan=lifespan,
                title=settings.title,
                version=settings.version,
                docs_url=settings.docs_url,
                redoc_url=None,
                contact={
                            "name": "Piotr",
                            "email": "pkrecz@poczta.onet.pl"})
registry.init_middleware(app)
