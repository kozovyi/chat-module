import uuid

from fastapi_users import FastAPIUsers

from modules.user.model import User
from modules.user.dependencies import get_user_manager
from modules.user.backend import auth_backend

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
