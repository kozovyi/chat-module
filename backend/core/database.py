from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Engine
from abc import ABC, abstractmethod

from core.config import settings


class Database(ABC):

    def __init__(
        self,
        url: str,
        pool_size: int = 5,
        max_overflow: int = 10,
        echo: bool = False,
        echo_pool: bool = False,
    ) -> None:

        self.engine: Engine | AsyncEngine
        self.session_factory: sessionmaker | async_sessionmaker

    @abstractmethod
    def dispose(self) -> None:
        pass

    @abstractmethod
    def session_getter(self):
        pass


class DatabaseHelperSync(Database):

    def __init__(
        self,
        url: str,
        pool_size: int,
        max_overflow: int,
        echo: bool,
        echo_pool: bool,
    ) -> None:
        super().__init__(url, pool_size, max_overflow, echo, echo_pool)
        self.engine = create_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            max_overflow=max_overflow,
            pool_size=pool_size,
        )

        self.session_factory = sessionmaker(
            bind=self.engine,
        )

    def dispose(self) -> None:
        self.engine.dispose()

    def session_getter(self):
        with self.session_factory() as session:
            yield session


class DatabaseHelperAsync(Database):

    def __init__(
        self,
        url: str,
        pool_size: int,
        max_overflow: int,
        echo: bool,
        echo_pool: bool,
    ) -> None:
        super().__init__(url, pool_size, max_overflow, echo, echo_pool)
        self.engine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            max_overflow=max_overflow,
            pool_size=pool_size,
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self):
        await self.engine.dispose()  # type: ignore

    async def session_getter(self):
        async with self.session_factory() as session:
            yield session


async_db_helper = DatabaseHelperAsync(
    url=settings.db.DB_URL_ASYNCPG,
    max_overflow=settings.db.max_overflow,
    pool_size=settings.db.pool_size,
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
)

sync_db_helper = DatabaseHelperSync(
    url=settings.db.DB_URL_PSYCOPG,
    max_overflow=settings.db.max_overflow,
    pool_size=settings.db.pool_size,
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
)

get_db = async_db_helper.session_getter