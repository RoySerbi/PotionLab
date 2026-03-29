from sqlmodel import Session, col, select

from app.models import Cocktail, CocktailIngredient, Ingredient
from app.schemas.cocktail import CocktailCreate


def _validate_ingredient_ids(session: Session, ingredient_ids: list[int]) -> None:
    if not ingredient_ids:
        return

    existing_ids = set(
        session.exec(
            select(Ingredient.id).where(col(Ingredient.id).in_(ingredient_ids))
        ).all()
    )
    missing_ids = sorted(set(ingredient_ids) - existing_ids)
    if missing_ids:
        raise ValueError(f"Ingredient id(s) not found: {missing_ids}")


def create_cocktail(session: Session, cocktail_in: CocktailCreate) -> Cocktail:
    try:
        _validate_ingredient_ids(
            session,
            [ingredient.ingredient_id for ingredient in cocktail_in.ingredients],
        )

        cocktail = Cocktail(
            name=cocktail_in.name,
            description=cocktail_in.description,
            instructions=cocktail_in.instructions,
            glass_type=cocktail_in.glass_type,
            difficulty=cocktail_in.difficulty,
        )
        session.add(cocktail)
        session.flush()
        if cocktail.id is None:
            raise RuntimeError("Cocktail ID was not generated")
        cocktail_id = cocktail.id

        for ingredient in cocktail_in.ingredients:
            session.add(
                CocktailIngredient(
                    cocktail_id=cocktail_id,
                    ingredient_id=ingredient.ingredient_id,
                    amount=ingredient.amount,
                    is_optional=ingredient.is_optional,
                )
            )

        session.commit()
        session.refresh(cocktail)
        return cocktail
    except Exception:
        session.rollback()
        raise


def read_cocktail_by_id(session: Session, id: int) -> Cocktail | None:
    cocktail = session.get(Cocktail, id)
    if not cocktail:
        return None

    return cocktail


def read_cocktail_ingredients(
    session: Session, cocktail_id: int
) -> tuple[list[dict[str, object]], list[str]]:
    links = session.exec(
        select(CocktailIngredient).where(CocktailIngredient.cocktail_id == cocktail_id)
    ).all()

    ingredient_ids = [link.ingredient_id for link in links]
    ingredient_by_id: dict[int, Ingredient] = {}
    if ingredient_ids:
        linked_ingredients = session.exec(
            select(Ingredient).where(col(Ingredient.id).in_(ingredient_ids))
        ).all()
        ingredient_by_id = {
            ingredient.id: ingredient
            for ingredient in linked_ingredients
            if ingredient.id is not None
        }

    ingredients_payload: list[dict[str, object]] = []
    flavor_profile: set[str] = set()

    for link in links:
        ingredient = ingredient_by_id.get(link.ingredient_id)
        if ingredient is None:
            continue
        ingredients_payload.append(
            {
                "ingredient_id": link.ingredient_id,
                "name": ingredient.name,
                "amount": link.amount,
                "is_optional": link.is_optional,
            }
        )
        flavor_profile.add(ingredient.category)

    return ingredients_payload, sorted(flavor_profile)


def read_all_cocktails(session: Session) -> list[Cocktail]:
    return list(session.exec(select(Cocktail)).all())


def update_cocktail(
    session: Session, id: int, cocktail_in: CocktailCreate
) -> Cocktail | None:
    cocktail = session.get(Cocktail, id)
    if not cocktail:
        return None

    try:
        _validate_ingredient_ids(
            session,
            [ingredient.ingredient_id for ingredient in cocktail_in.ingredients],
        )

        cocktail.name = cocktail_in.name
        cocktail.description = cocktail_in.description
        cocktail.instructions = cocktail_in.instructions
        cocktail.glass_type = cocktail_in.glass_type
        cocktail.difficulty = cocktail_in.difficulty

        existing_links = session.exec(
            select(CocktailIngredient).where(CocktailIngredient.cocktail_id == id)
        ).all()
        for link in existing_links:
            session.delete(link)

        for ingredient in cocktail_in.ingredients:
            session.add(
                CocktailIngredient(
                    cocktail_id=id,
                    ingredient_id=ingredient.ingredient_id,
                    amount=ingredient.amount,
                    is_optional=ingredient.is_optional,
                )
            )

        session.add(cocktail)
        session.commit()
        session.refresh(cocktail)
        return cocktail
    except Exception:
        session.rollback()
        raise


def delete_cocktail(session: Session, id: int) -> bool:
    cocktail = session.get(Cocktail, id)
    if not cocktail:
        return False

    try:
        existing_links = session.exec(
            select(CocktailIngredient).where(CocktailIngredient.cocktail_id == id)
        ).all()
        for link in existing_links:
            session.delete(link)

        session.delete(cocktail)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
