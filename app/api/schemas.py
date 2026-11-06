import uuid

import pydantic


class UserCreate(pydantic.BaseModel):
    name: pydantic.constr(min_length=1, max_length=100)  # type: ignore[valid-type]
    email: pydantic.EmailStr
