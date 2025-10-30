import uuid
from fastapi_users import FastAPIUsers

from core.models.user import User
from core.auth.manager import UserManager
from core.auth.backend import auth_backend

fastapi_users = FastAPIUsers[User, uuid.UUID](
    UserManager.get_user_manager,
    [auth_backend],
)