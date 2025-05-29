# ruff: noqa: F401
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, Session
from app.core.config import settings
from typing import Generator

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
