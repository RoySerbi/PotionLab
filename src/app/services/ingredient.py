"""Ingredient service layer - business logic for ingredient operations."""

from sqlmodel import Session, select

from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientCreate


def create_ingredient(session: Session, ingredient_in: IngredientCreate) -> Ingredient:
    """
    Create a new ingredient in the database.

    Args:
        session: Database session
        ingredient_in: Ingredient data from request

    Returns:
        Created Ingredient model instance
    """
    ingredient = Ingredient(
        name=ingredient_in.name,
        category=ingredient_in.category,
        description=ingredient_in.description,
    )
    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)
    return ingredient


def read_ingredient_by_id(session: Session, ingredient_id: int) -> Ingredient | None:
    """
    Retrieve a single ingredient by ID.

    Args:
        session: Database session
        ingredient_id: ID of the ingredient to retrieve

    Returns:
        Ingredient model instance or None if not found
    """
    return session.get(Ingredient, ingredient_id)


def read_all_ingredients(session: Session) -> list[Ingredient]:
    """
    Retrieve all ingredients from the database.

    Args:
        session: Database session

    Returns:
        List of all Ingredient model instances
    """
    statement = select(Ingredient)
    results = session.exec(statement)
    return list(results.all())


def update_ingredient(
    session: Session, ingredient_id: int, ingredient_in: IngredientCreate
) -> Ingredient | None:
    """
    Update an existing ingredient.

    Args:
        session: Database session
        ingredient_id: ID of the ingredient to update
        ingredient_in: New ingredient data

    Returns:
        Updated Ingredient model instance or None if not found
    """
    ingredient = session.get(Ingredient, ingredient_id)
    if not ingredient:
        return None

    ingredient.name = ingredient_in.name
    ingredient.category = ingredient_in.category
    ingredient.description = ingredient_in.description

    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)
    return ingredient


def delete_ingredient(session: Session, ingredient_id: int) -> bool:
    """
    Delete an ingredient from the database.

    Args:
        session: Database session
        ingredient_id: ID of the ingredient to delete

    Returns:
        True if deleted, False if not found
    """
    ingredient = session.get(Ingredient, ingredient_id)
    if not ingredient:
        return False

    session.delete(ingredient)
    session.commit()
    return True
