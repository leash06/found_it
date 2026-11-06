import sqlalchemy.exc
from foundit_db.models import User
from foundit_db.users import AsyncQuerier


class DuplicateEmailError(Exception):
    pass


async def create_user(
    querier: AsyncQuerier, *, name: str, email: str
) -> User:
    try:
        user = await querier.create_user(name=name, email=email)
    except sqlalchemy.exc.IntegrityError as exc:
        # users_email_lower_key: unique on lower(email) -> 409, never 500.
        if "users_email_lower_key" in str(exc.orig):
            raise DuplicateEmailError(email) from exc
        raise
    if user is None:
        raise RuntimeError("CreateUser returned no row")
    return user


async def get_user(
    querier: AsyncQuerier, *, id_user: object
) -> User | None:
    return await querier.get_user_by_id(id_user=id_user)  # type: ignore[arg-type]
