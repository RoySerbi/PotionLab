"""FlavorTag service layer - business logic for flavor tag operations."""

from sqlmodel import Session, select

from app.models.flavor_tag import FlavorTag
from app.schemas.flavor_tag import FlavorTagCreate


def create_flavor_tag(session: Session, flavor_tag_in: FlavorTagCreate) -> FlavorTag:
    """
    Create a new flavor tag in the database.

    Args:
        session: Database session
        flavor_tag_in: FlavorTag data from request

    Returns:
        Created FlavorTag model instance
    """
    flavor_tag = FlavorTag(
        name=flavor_tag_in.name,
        category=flavor_tag_in.category,
    )
    session.add(flavor_tag)
    session.commit()
    session.refresh(flavor_tag)
    return flavor_tag


def read_flavor_tag_by_id(session: Session, flavor_tag_id: int) -> FlavorTag | None:
    """
    Retrieve a single flavor tag by ID.

    Args:
        session: Database session
        flavor_tag_id: ID of the flavor tag to retrieve

    Returns:
        FlavorTag model instance or None if not found
    """
    return session.get(FlavorTag, flavor_tag_id)


def read_all_flavor_tags(session: Session) -> list[FlavorTag]:
    """
    Retrieve all flavor tags from the database.

    Args:
        session: Database session

    Returns:
        List of all FlavorTag model instances
    """
    statement = select(FlavorTag)
    results = session.exec(statement)
    return list(results.all())


def update_flavor_tag(
    session: Session, flavor_tag_id: int, flavor_tag_in: FlavorTagCreate
) -> FlavorTag | None:
    """
    Update an existing flavor tag.

    Args:
        session: Database session
        flavor_tag_id: ID of the flavor tag to update
        flavor_tag_in: New flavor tag data

    Returns:
        Updated FlavorTag model instance or None if not found
    """
    flavor_tag = session.get(FlavorTag, flavor_tag_id)
    if not flavor_tag:
        return None

    flavor_tag.name = flavor_tag_in.name
    flavor_tag.category = flavor_tag_in.category

    session.add(flavor_tag)
    session.commit()
    session.refresh(flavor_tag)
    return flavor_tag


def delete_flavor_tag(session: Session, flavor_tag_id: int) -> bool:
    """
    Delete a flavor tag from the database.

    Args:
        session: Database session
        flavor_tag_id: ID of the flavor tag to delete

    Returns:
        True if deleted, False if not found
    """
    flavor_tag = session.get(FlavorTag, flavor_tag_id)
    if not flavor_tag:
        return False

    session.delete(flavor_tag)
    session.commit()
    return True
