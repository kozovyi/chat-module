from uuid import uuid4
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy import delete 

from modules.user.model import User
from modules.user.fastapi_users import current_active_user
from modules.chat.manager import redis_manager

