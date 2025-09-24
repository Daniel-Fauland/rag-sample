from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from config import config


engine = create_async_engine(
    config.db_uri,
    echo=config.db_echo,
    # Connection pool configuration for scalability
    # Number of connections to maintain in pool
    pool_size=config.db_pool_size,
    # Additional connections when pool is full
    max_overflow=config.db_max_overflow,
    # Validate connections before use
    pool_pre_ping=True,
    # Recycle connections after specified time
    pool_recycle=config.db_pool_recycle,
    # Timeout waiting for available connection
    pool_timeout=config.db_pool_timeout,
    # Reset connection state on return
    pool_reset_on_return='commit',
    # Performance optimizations
    # Don't log pool operations (set to True for debugging)
    echo_pool=False,
    # Connection arguments
    connect_args={
        "ssl": config.db_ssl
    }
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:  # type: ignore
    Session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    async with Session() as session:
        yield session


async def get_test_session() -> AsyncSession:  # type: ignore
    """Get a database session specifically for tests.

    This version disposes the engine after each session to prevent
    asyncio loop conflicts in tests, but should NOT be used in production.
    """
    Session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    async with Session() as session:
        yield session
    # Only dispose in test environment to prevent loop conflicts
    await engine.dispose()


async def get_session_direct() -> AsyncSession:
    """Get a database session directly without using dependency injection.

    This function is intended for use outside of FastAPI routes, such as in
    startup/shutdown events or background tasks.

    Returns:
        AsyncSession: A database session

    Note:
        The caller is responsible for closing this session when done.
    """
    Session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    return Session()
