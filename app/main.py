import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import health as health_api
from app.api import users as users_api
from app.config import settings
from app.db.engine import create_engine
from app.services.users import DuplicateEmailError

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # The single async pool for the whole process; closed on shutdown.
    app.state.engine = create_engine()
    yield
    await app.state.engine.dispose()


app = FastAPI(title="FoundIt API", version="0.1.0", lifespan=lifespan)


@app.exception_handler(DuplicateEmailError)
async def duplicate_email_handler(request: Request, exc: DuplicateEmailError):
    return JSONResponse(
        status_code=409, content={"detail": "Email already registered"}
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled error: %s %s", request.method, request.url.path
    )
    return JSONResponse(
        status_code=500, content={"detail": "Internal server error"}
    )


app.include_router(health_api.router)
app.include_router(users_api.router)
