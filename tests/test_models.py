import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.models import (
    Cocktail,
    CocktailIngredient,
    Ingredient,
)


def test_cocktail_ingredient_composite_pk_prevents_duplicates(session: Session):
    cocktail = Cocktail(
        name="Mojito",
        description="Classic Cuban cocktail",
        instructions="Muddle mint and lime, add rum, soda water, ice",
        glass_type="Highball",
        difficulty=2,
    )
    ingredient = Ingredient(
        name="White Rum",
        category="Spirit",
        description="Light-bodied rum",
    )
    session.add(cocktail)
    session.add(ingredient)
    session.commit()
    session.refresh(cocktail)
    session.refresh(ingredient)

    link1 = CocktailIngredient(
        cocktail_id=cocktail.id,
        ingredient_id=ingredient.id,
        amount="2 oz",
        is_optional=False,
    )
    session.add(link1)
    session.commit()

    link2 = CocktailIngredient(
        cocktail_id=cocktail.id,
        ingredient_id=ingredient.id,
        amount="3 oz",
        is_optional=True,
    )
    session.add(link2)

    with pytest.raises(IntegrityError):
        session.commit()
