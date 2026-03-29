from collections.abc import Generator

from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings
from app.models import (  # noqa: F401
    Cocktail,
    CocktailIngredient,
    FlavorTag,
    Ingredient,
    IngredientFlavorTag,
    User,
)


def get_db_url() -> str:
    """Get database URL, respecting SQLMODEL_DATABASE env var for tests."""
    import os

    return os.environ.get(
        "SQLMODEL_DATABASE", settings.database_url or "sqlite:///data/app.db"
    )


def get_engine() -> Engine:
    """Create database engine with dual-mode support (PostgreSQL or SQLite)."""
    db_url = get_db_url()
    if db_url.startswith("postgresql"):
        return create_engine(db_url, echo=False, pool_pre_ping=True)
    else:
        return create_engine(
            db_url, echo=False, connect_args={"check_same_thread": False}
        )


engine = get_engine()


def init_db() -> None:
    """Create all tables in the database."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency to get a database session."""
    with Session(engine) as session:
        yield session
