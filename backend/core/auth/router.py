from typing import Generic
import uuid

from fastapi_users import FastAPIUsers
from fastapi_users import models

from core.models.user import User
from core.auth.manager import UserManager
from core.auth.backend import auth_backend


class FastAPIUsersRefresh(FastAPIUsers, Generic[models.UP, models.ID]):
    pass

fastapi_users = FastAPIUsersRefresh[User, uuid.UUID](
    UserManager.get_user_manager,
    [auth_backend],
)

