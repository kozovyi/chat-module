from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from pathlib import Path
from typing import Literal

BASE_DIR = Path(__file__).parent

class DatabaseConfig(BaseModel):
    HOST: str
    PASS: str
    NAME: str
    PORT: str
    USER: str

    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def DB_URL_ASYNCPG(self):
        return f"postgresql+asyncpg://{self.USER}:{self.PASS}@{self.HOST}:{self.PORT}/{self.NAME}"

    @property
    def DB_URL_PSYCOPG(self):
        return f"postgresql+psycopg://{self.USER}:{self.PASS}@{self.HOST}:{self.PORT}/{self.NAME}"

class MongoConfig(BaseModel):
    PASS: str
    USER: str

class AccessToken(BaseModel):
    lifetime_seconds: int = 3600
    reset_password_token_secret: str
    verification_token_secret: str

class ApiV1Prefix:
    prefix: str = "/api_v1"
    user: str = "/user"
    auth: str = "/auth"
    messages: str = "/messages"

class ApiPrefix:
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()

    @property
    def bearer_token_url(self) -> str:
        return self.prefix.removeprefix("/") + self.v1.prefix + self.v1.auth + "/login"


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000

class RunGunicorn(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 2
    timeout: int = 900

class LoggingConfig(BaseModel):
    log_level: Literal['debug', 'info', 'warning', 'error', 'critical'] = 'info'
    log_format: str = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'


class SuperUser(BaseModel):
    default_email: str
    default_password: str
    default_is_active: bool
    default_is_superuser: bool
    default_is_verified: bool

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            "core/.env.template",
            "core/.env",
        ),
        extra="ignore",
        case_sensitive=False,
        env_nested_delimiter="__",  # після цього роздільника шукати значення
        env_prefix="APP_CONFIG__",  # префікс для точного знаходження значення
    )
    run: RunConfig = RunConfig()
    run_gunicorn: RunGunicorn = RunGunicorn()
    api: ApiPrefix = ApiPrefix()
    logger: LoggingConfig = LoggingConfig()
    access_token: AccessToken
    super_user: SuperUser
    db: DatabaseConfig
    mongo_db: MongoConfig


settings = Settings() # type: ignore
