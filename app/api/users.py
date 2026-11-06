import uuid

from fastapi import APIRouter, HTTPException

from app.api.schemas import UserCreate
from app.db.engine import QuerierDep
from app.services import users as users_service
from foundit_db import models

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", status_code=201, response_model=models.User)
async def create_user(body: UserCreate, querier: QuerierDep) -> models.User:
    user = await users_service.create_user(querier, name=body.name, email=body.email)
    return user


@router.get("/{id_user}", response_model=models.User)
async def get_user(id_user: uuid.UUID, querier: QuerierDep) -> models.User:
    user = await users_service.get_user(querier, id_user=id_user)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
