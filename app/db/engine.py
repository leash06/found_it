import logging
from collections.abc import AsyncIterator
from typing import Annotated

import sqlalchemy
import sqlalchemy.ext.asyncio
from fastapi import Depends, Request

from foundit_db import models  # noqa: F401  (keeps generated package import intact)
from foundit_db.users import AsyncQuerier

logger = logging.getLogger(__name__)


def create_engine() -> sqlalchemy.ext.asyncio.AsyncEngine:
    from app.config import settings

    return sqlalchemy.ext.asyncio.create_async_engine(
        settings.database_url, pool_pre_ping=True
    )


# One pool lives on app.state.engine (created once in the lifespan in app/main.py,
# disposed at shutdown). Each request checks out one connection inside a single
# transaction, so a failed request rolls back automatically on exit.
async def get_connection(
    request: Request,
) -> AsyncIterator[sqlalchemy.ext.asyncio.AsyncConnection]:
    async with request.app.state.engine.begin() as conn:
        yield conn


def get_querier(
    conn: Annotated[sqlalchemy.ext.asyncio.AsyncConnection, Depends(get_connection)],
) -> AsyncQuerier:
    return AsyncQuerier(conn)


QuerierDep = Annotated[AsyncQuerier, Depends(get_querier)]
