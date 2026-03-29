from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.core.security import require_role
from app.db.session import get_session
from app.schemas.cocktail import CocktailCreate, CocktailRead, CocktailReadFull
from app.services.cocktail import (
    create_cocktail,
    delete_cocktail,
    read_all_cocktails,
    read_cocktail_by_id,
    read_cocktail_ingredients,
    update_cocktail,
)

router = APIRouter(tags=["cocktails"])


@router.post(
    "/cocktails", status_code=status.HTTP_201_CREATED, response_model=CocktailRead
)
def create_cocktail_endpoint(
    cocktail_in: CocktailCreate,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(require_role(["editor", "admin"])),
) -> CocktailRead:
    try:
        cocktail = create_cocktail(session, cocktail_in)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid cocktail data"
        ) from exc
    return CocktailRead.model_validate(cocktail)


@router.get(
    "/cocktails", status_code=status.HTTP_200_OK, response_model=list[CocktailRead]
)
def list_cocktails(session: Session = Depends(get_session)) -> list[CocktailRead]:
    cocktails = read_all_cocktails(session)
    return [CocktailRead.model_validate(cocktail) for cocktail in cocktails]


@router.get(
    "/cocktails/{cocktail_id}",
    status_code=status.HTTP_200_OK,
    response_model=CocktailReadFull,
)
def get_cocktail(
    cocktail_id: int,
    session: Session = Depends(get_session),
) -> CocktailReadFull:
    cocktail = read_cocktail_by_id(session, cocktail_id)
    if not cocktail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cocktail with id {cocktail_id} not found",
        )
    if cocktail.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cocktail has no identifier",
        )
    ingredients, flavor_profile = read_cocktail_ingredients(session, cocktail_id)
    return CocktailReadFull(
        id=cocktail.id,
        name=cocktail.name,
        description=cocktail.description,
        instructions=cocktail.instructions,
        glass_type=cocktail.glass_type,
        difficulty=cocktail.difficulty,
        ingredients=ingredients,
        flavor_profile=flavor_profile,
    )


@router.put(
    "/cocktails/{cocktail_id}",
    status_code=status.HTTP_200_OK,
    response_model=CocktailRead,
)
def update_cocktail_endpoint(
    cocktail_id: int,
    cocktail_in: CocktailCreate,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(require_role(["editor", "admin"])),
) -> CocktailRead:
    try:
        cocktail = update_cocktail(session, cocktail_id, cocktail_in)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid cocktail data"
        ) from exc

    if not cocktail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cocktail with id {cocktail_id} not found",
        )
    return CocktailRead.model_validate(cocktail)


@router.delete("/cocktails/{cocktail_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cocktail_endpoint(
    cocktail_id: int,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(require_role(["editor", "admin"])),
) -> None:
    deleted = delete_cocktail(session, cocktail_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cocktail with id {cocktail_id} not found",
        )
