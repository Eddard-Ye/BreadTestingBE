from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.db.base import Base

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        engine_kwargs: dict = {
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        }
        if settings.database_url.startswith("sqlite"):
            engine_kwargs["connect_args"] = {"check_same_thread": False}
            if settings.database_url.endswith(":memory:"):
                engine_kwargs["poolclass"] = StaticPool
        _engine = create_engine(settings.database_url, **engine_kwargs)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    return _SessionLocal


def reset_database_runtime() -> None:
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None


def get_db() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    from app.models.measurement import MeasurementRecord  # noqa: F401
    from app.models.recipe import Recipe  # noqa: F401

    Base.metadata.create_all(bind=get_engine())
