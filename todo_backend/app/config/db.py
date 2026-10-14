from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .settings import setting

engine = create_async_engine(
    setting.DATABASE_URL,
    echo=True,  # to print sql query during development
    pool_size=20,  # how many pool will stay open at a time
    max_overflow=10,  # allows up to 10 extra temporary connections during sudden traffic spikes
    pool_pre_ping=True,  # check auto re-connect db after every 30mins that prevents memory leaks
    connect_args={"ssl": "require"},
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,  # Prevents unnecessary database re-fetches after a commit
    expire_on_commit=False,
)


# for sqlalchemy model
class Base(DeclarativeBase):
    pass


# dependency generator to cleanly inject the DB session into routes
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
