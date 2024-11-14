from fastapi import FastAPI

from env import DEBUG_MODE
from logger import logger
from middleware.logger import LoggerMiddleWare

from routes.router import root_router, v1_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="CaizzzAI API",
        version="0.0.1",
        redoc_url="/redoc" if DEBUG_MODE else None,
        docs_url="/docs" if DEBUG_MODE else None,
        openapi_url="/openapi.json" if DEBUG_MODE else None,
    )

    # add routers
    app.include_router(root_router)
    app.include_router(v1_router)

    # add middlewares
    app.add_middleware(LoggerMiddleWare)

    logger.info("Init app successfully")
    return app
