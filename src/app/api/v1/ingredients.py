"""Ingredient CRUD API endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.security import require_role
from app.db.session import get_session
from app.schemas.ingredient import (
    IngredientCreate,
    IngredientRead,
    IngredientReadWithTags,
)
from app.services.ingredient import (
    create_ingredient,
    delete_ingredient,
    read_all_ingredients,
    read_ingredient_by_id,
    update_ingredient,
)

router = APIRouter(tags=["ingredients"])


@router.post(
    "/ingredients", status_code=status.HTTP_201_CREATED, response_model=IngredientRead
)
def create_ingredient_endpoint(
    ingredient_in: IngredientCreate,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(require_role(["editor", "admin"])),
) -> IngredientRead:
    """Create a new ingredient."""
    ingredient = create_ingredient(session, ingredient_in)
    return IngredientRead.model_validate(ingredient)


@router.get("/ingredients", status_code=status.HTTP_200_OK)
def list_ingredients(
    session: Session = Depends(get_session),
) -> list[IngredientRead]:
    """List all ingredients (flat schema without relationships)."""
    ingredients = read_all_ingredients(session)
    return [IngredientRead.model_validate(ing) for ing in ingredients]


@router.get(
    "/ingredients/{ingredient_id}",
    status_code=status.HTTP_200_OK,
    response_model=IngredientReadWithTags,
)
def get_ingredient(
    ingredient_id: int,
    session: Session = Depends(get_session),
) -> IngredientReadWithTags:
    """Get a single ingredient by ID (nested schema with flavor tags)."""
    ingredient = read_ingredient_by_id(session, ingredient_id)
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with id {ingredient_id} not found",
        )
    return IngredientReadWithTags.model_validate(ingredient)


@router.put(
    "/ingredients/{ingredient_id}",
    status_code=status.HTTP_200_OK,
    response_model=IngredientRead,
)
def update_ingredient_endpoint(
    ingredient_id: int,
    ingredient_in: IngredientCreate,
    session: Session = Depends(get_session),
) -> IngredientRead:
    """Update an existing ingredient."""
    ingredient = update_ingredient(session, ingredient_id, ingredient_in)
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with id {ingredient_id} not found",
        )
    return IngredientRead.model_validate(ingredient)


@router.delete("/ingredients/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient_endpoint(
    ingredient_id: int,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(require_role(["editor", "admin"])),
) -> None:
    """Delete an ingredient."""
    deleted = delete_ingredient(session, ingredient_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with id {ingredient_id} not found",
        )
