from sqlalchemy import Engine
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass

def create_all_tables(engine: Engine) -> None:
    """
    Creates every table defined via this Base that doesn't already exist yet.
    """
    import app.models  # noqa: F401 - registers all models on Base.metadata

    Base.metadata.create_all(bind=engine)