import logging

import sqlalchemy
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=None)
async def health(request: Request):
    try:
        async with request.app.state.engine.connect() as conn:
            await conn.execute(sqlalchemy.text("SELECT 1"))
    except Exception:
        logger.exception("Health check: database unreachable")
        return JSONResponse(status_code=503, content={"status": "unhealthy"})
    return {"status": "ok", "database": "ok"}
