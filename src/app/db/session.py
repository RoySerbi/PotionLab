from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings
from app.models import (  # noqa: F401
    Cocktail,
    CocktailIngredient,
    FlavorTag,
    Ingredient,
    IngredientFlavorTag,
)


def get_db_url() -> str:
    """Get database URL, respecting SQLMODEL_DATABASE env var for tests."""
    import os

    return os.environ.get("SQLMODEL_DATABASE", settings.database_url)


engine = create_engine(
    get_db_url(),
    echo=False,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """Create all tables in the database."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency to get a database session."""
    with Session(engine) as session:
        yield session
