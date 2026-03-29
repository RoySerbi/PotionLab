"""FlavorTag CRUD API endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.core.security import require_role
from app.db.session import get_session
from app.schemas.flavor_tag import FlavorTagCreate, FlavorTagRead
from app.services.flavor_tag import (
    create_flavor_tag,
    delete_flavor_tag,
    read_all_flavor_tags,
    read_flavor_tag_by_id,
    update_flavor_tag,
)

router = APIRouter(tags=["flavor-tags"])


@router.post(
    "/flavor-tags", status_code=status.HTTP_201_CREATED, response_model=FlavorTagRead
)
def create_flavor_tag_endpoint(
    flavor_tag_in: FlavorTagCreate,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> FlavorTagRead:
    """Create a new flavor tag."""
    try:
        flavor_tag = create_flavor_tag(session, flavor_tag_in)
        return FlavorTagRead.model_validate(flavor_tag)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"FlavorTag with name '{flavor_tag_in.name}' already exists",
        )


@router.get("/flavor-tags", status_code=status.HTTP_200_OK)
def list_flavor_tags(
    session: Session = Depends(get_session),
) -> list[FlavorTagRead]:
    """List all flavor tags."""
    flavor_tags = read_all_flavor_tags(session)
    return [FlavorTagRead.model_validate(ft) for ft in flavor_tags]


@router.get(
    "/flavor-tags/{flavor_tag_id}",
    status_code=status.HTTP_200_OK,
    response_model=FlavorTagRead,
)
def get_flavor_tag(
    flavor_tag_id: int,
    session: Session = Depends(get_session),
) -> FlavorTagRead:
    """Get a single flavor tag by ID."""
    flavor_tag = read_flavor_tag_by_id(session, flavor_tag_id)
    if not flavor_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FlavorTag with id {flavor_tag_id} not found",
        )
    return FlavorTagRead.model_validate(flavor_tag)


@router.put(
    "/flavor-tags/{flavor_tag_id}",
    status_code=status.HTTP_200_OK,
    response_model=FlavorTagRead,
)
def update_flavor_tag_endpoint(
    flavor_tag_id: int,
    flavor_tag_in: FlavorTagCreate,
    session: Session = Depends(get_session),
) -> FlavorTagRead:
    """Update an existing flavor tag."""
    try:
        flavor_tag = update_flavor_tag(session, flavor_tag_id, flavor_tag_in)
        if not flavor_tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FlavorTag with id {flavor_tag_id} not found",
            )
        return FlavorTagRead.model_validate(flavor_tag)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"FlavorTag with name '{flavor_tag_in.name}' already exists",
        )


@router.delete("/flavor-tags/{flavor_tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flavor_tag_endpoint(
    flavor_tag_id: int,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> None:
    """Delete a flavor tag."""
    deleted = delete_flavor_tag(session, flavor_tag_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FlavorTag with id {flavor_tag_id} not found",
        )
