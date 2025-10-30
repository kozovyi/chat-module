from fastapi_users.authentication import AuthenticationBackend

from core.auth.transport import bearer_transport
from core.auth.strategy import get_database_strategy

auth_backend = AuthenticationBackend(
    name="jwt-db",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)