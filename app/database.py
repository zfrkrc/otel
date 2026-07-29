from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


_engine = None
_session_maker = None


def get_session_maker():
    global _session_maker
    if _session_maker is None:
        raise RuntimeError("DB not initialized")
    return _session_maker


async def init_db():
    global _engine, _session_maker
    from app.config import get_settings
    settings = get_settings()
    _engine = create_async_engine(settings.database_url, echo=settings.debug)
    _session_maker = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    global _engine, _session_maker
    if _engine:
        await _engine.dispose()
        _engine = None
        _session_maker = None
