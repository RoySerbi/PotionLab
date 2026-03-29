"""Service layer unit tests for cocktail business logic."""

import pytest
from sqlmodel import Session

from app.models import Ingredient
from app.schemas.cocktail import CocktailCreate, CocktailIngredientCreate
from app.services.cocktail import (
    create_cocktail,
    delete_cocktail,
    read_all_cocktails,
    read_cocktail_by_id,
    read_cocktail_ingredients,
    update_cocktail,
)


def test_create_cocktail_validates_ingredient_ids(session: Session):
    """Test create_cocktail raises ValueError for invalid ingredient_id."""
    cocktail_in = CocktailCreate(
        name="Bad Cocktail",
        description="Test",
        instructions="Test",
        glass_type="Rocks",
        difficulty=1,
        ingredients=[
            CocktailIngredientCreate(
                ingredient_id=9999, amount="1 oz", is_optional=False
            )
        ],
    )
    with pytest.raises(ValueError, match="Ingredient id.*not found"):
        create_cocktail(session, cocktail_in)


def test_create_cocktail_with_valid_ingredient(session: Session):
    """Test create_cocktail succeeds with valid ingredient_id."""
    ingredient = Ingredient(name="Gin", category="spirit", description="Dry gin")
    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)

    if ingredient.id is None:
        pytest.fail("Ingredient ID was not generated")

    cocktail_in = CocktailCreate(
        name="Gin Martini",
        description="Classic",
        instructions="Stir with ice",
        glass_type="Martini",
        difficulty=2,
        ingredients=[
            CocktailIngredientCreate(
                ingredient_id=ingredient.id, amount="2.5 oz", is_optional=False
            )
        ],
    )
    cocktail = create_cocktail(session, cocktail_in)
    assert cocktail.id is not None
    assert cocktail.name == "Gin Martini"


def test_create_cocktail_with_multiple_missing_ingredients(session: Session):
    """Test create_cocktail reports all missing ingredient_ids."""
    cocktail_in = CocktailCreate(
        name="Multi Bad",
        description="Test",
        instructions="Test",
        glass_type="Rocks",
        difficulty=1,
        ingredients=[
            CocktailIngredientCreate(
                ingredient_id=111, amount="1 oz", is_optional=False
            ),
            CocktailIngredientCreate(
                ingredient_id=222, amount="1 oz", is_optional=False
            ),
        ],
    )
    with pytest.raises(ValueError, match="111.*222"):
        create_cocktail(session, cocktail_in)


def test_read_cocktail_by_id_not_found(session: Session):
    """Test read_cocktail_by_id returns None for missing cocktail."""
    result = read_cocktail_by_id(session, 9999)
    assert result is None


def test_read_cocktail_by_id_success(session: Session):
    """Test read_cocktail_by_id returns cocktail for valid id."""
    ingredient = Ingredient(name="Vodka", category="spirit", description="Neutral")
    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)

    if ingredient.id is None:
        pytest.fail("Ingredient ID was not generated")

    cocktail_in = CocktailCreate(
        name="Vodka Martini",
        description="Shaken",
        instructions="Shake",
        glass_type="Martini",
        difficulty=2,
        ingredients=[
            CocktailIngredientCreate(
                ingredient_id=ingredient.id, amount="2.5 oz", is_optional=False
            )
        ],
    )
    cocktail = create_cocktail(session, cocktail_in)
    if cocktail.id is None:
        pytest.fail("Cocktail ID was not generated")

    found = read_cocktail_by_id(session, cocktail.id)
    assert found is not None
    assert found.name == "Vodka Martini"


def test_read_cocktail_ingredients(session: Session):
    """Test read_cocktail_ingredients returns ingredients and flavor_profile."""
    ing_one = Ingredient(name="Rum", category="spirit", description="Caribbean rum")
    ing_two = Ingredient(name="Lime Juice", category="citrus", description="Fresh lime")
    session.add(ing_one)
    session.add(ing_two)
    session.commit()
    session.refresh(ing_one)
    session.refresh(ing_two)

    if ing_one.id is None or ing_two.id is None:
        pytest.fail("Ingredient IDs were not generated")

    cocktail_in = CocktailCreate(
        name="Daiquiri",
        description="Classic",
        instructions="Shake",
        glass_type="Coupe",
        difficulty=2,
        ingredients=[
            CocktailIngredientCreate(
                ingredient_id=ing_one.id, amount="2 oz", is_optional=False
            ),
            CocktailIngredientCreate(
                ingredient_id=ing_two.id, amount="0.75 oz", is_optional=False
            ),
        ],
    )
    cocktail = create_cocktail(session, cocktail_in)
    if cocktail.id is None:
        pytest.fail("Cocktail ID was not generated")

    ingredients_payload, flavor_profile = read_cocktail_ingredients(
        session, cocktail.id
    )
    assert len(ingredients_payload) == 2
    assert set(flavor_profile) == {"citrus", "spirit"}
    assert {item["name"] for item in ingredients_payload} == {"Rum", "Lime Juice"}


def test_read_all_cocktails(session: Session):
    """Test read_all_cocktails returns all cocktails."""
    ingredient = Ingredient(name="Whiskey", category="spirit", description="Bourbon")
    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)

    if ingredient.id is None:
        pytest.fail("Ingredient ID was not generated")

    cocktail_in_one = CocktailCreate(
        name="Old Fashioned",
        description="Classic",
        instructions="Stir",
        glass_type="Rocks",
        difficulty=2,
        ingredients=[
            CocktailIngredientCreate(
                ingredient_id=ingredient.id, amount="2 oz", is_optional=False
            )
        ],
    )
    cocktail_in_two = CocktailCreate(
        name="Manhattan",
        description="Classic",
        instructions="Stir",
        glass_type="Coupe",
        difficulty=3,
        ingredients=[
            CocktailIngredientCreate(
                ingredient_id=ingredient.id, amount="2 oz", is_optional=False
            )
        ],
    )
    create_cocktail(session, cocktail_in_one)
    create_cocktail(session, cocktail_in_two)

    cocktails = read_all_cocktails(session)
    assert len(cocktails) >= 2
    names = {c.name for c in cocktails}
    assert "Old Fashioned" in names
    assert "Manhattan" in names


def test_update_cocktail_validates_ingredient_ids(session: Session):
    """Test update_cocktail raises ValueError for invalid ingredient_id."""
    ingredient = Ingredient(name="Tequila", category="spirit", description="Blanco")
    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)

    if ingredient.id is None:
        pytest.fail("Ingredient ID was not generated")

    cocktail_in = CocktailCreate(
        name="Margarita",
        description="Classic",
        instructions="Shake",
        glass_type="Coupe",
        difficulty=2,
        ingredients=[
            CocktailIngredientCreate(
                ingredient_id=ingredient.id, amount="2 oz", is_optional=False
            )
        ],
    )
    cocktail = create_cocktail(session, cocktail_in)
    if cocktail.id is None:
        pytest.fail("Cocktail ID was not generated")

    update_in = CocktailCreate(
        name="Margarita Updated",
        description="Updated",
        instructions="Shake",
        glass_type="Coupe",
        difficulty=2,
        ingredients=[
            CocktailIngredientCreate(
                ingredient_id=9999, amount="2 oz", is_optional=False
            )
        ],
    )
    with pytest.raises(ValueError, match="Ingredient id.*not found"):
        update_cocktail(session, cocktail.id, update_in)


def test_update_cocktail_not_found(session: Session):
    """Test update_cocktail returns None for missing cocktail."""
    cocktail_in = CocktailCreate(
        name="Ghost",
        description="Does not exist",
        instructions="N/A",
        glass_type="Rocks",
        difficulty=1,
        ingredients=[],
    )
    result = update_cocktail(session, 9999, cocktail_in)
    assert result is None


def test_update_cocktail_success(session: Session):
    """Test update_cocktail updates cocktail and replaces ingredients."""
    ing_one = Ingredient(name="Brandy", category="spirit", description="Cognac")
    ing_two = Ingredient(
        name="Lemon Juice", category="citrus", description="Fresh lemon"
    )
    session.add(ing_one)
    session.add(ing_two)
    session.commit()
    session.refresh(ing_one)
    session.refresh(ing_two)

    if ing_one.id is None or ing_two.id is None:
        pytest.fail("Ingredient IDs were not generated")

    cocktail_in = CocktailCreate(
        name="Sidecar",
        description="Classic",
        instructions="Shake",
        glass_type="Coupe",
        difficulty=2,
        ingredients=[
            CocktailIngredientCreate(
                ingredient_id=ing_one.id, amount="2 oz", is_optional=False
            )
        ],
    )
    cocktail = create_cocktail(session, cocktail_in)
    if cocktail.id is None:
        pytest.fail("Cocktail ID was not generated")

    update_in = CocktailCreate(
        name="Sidecar Updated",
        description="Updated classic",
        instructions="Shake vigorously",
        glass_type="Coupe",
        difficulty=3,
        ingredients=[
            CocktailIngredientCreate(
                ingredient_id=ing_one.id, amount="1.5 oz", is_optional=False
            ),
            CocktailIngredientCreate(
                ingredient_id=ing_two.id, amount="0.75 oz", is_optional=False
            ),
        ],
    )
    updated = update_cocktail(session, cocktail.id, update_in)
    assert updated is not None
    assert updated.name == "Sidecar Updated"
    assert updated.difficulty == 3

    ingredients_payload, _ = read_cocktail_ingredients(session, cocktail.id)
    assert len(ingredients_payload) == 2


def test_delete_cocktail_not_found(session: Session):
    """Test delete_cocktail returns False for missing cocktail."""
    result = delete_cocktail(session, 9999)
    assert result is False


def test_delete_cocktail_success(session: Session):
    """Test delete_cocktail removes cocktail and related ingredients."""
    ingredient = Ingredient(name="Gin", category="spirit", description="London Dry")
    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)

    if ingredient.id is None:
        pytest.fail("Ingredient ID was not generated")

    cocktail_in = CocktailCreate(
        name="Gin Fizz",
        description="Fizzy",
        instructions="Shake and top with soda",
        glass_type="Highball",
        difficulty=1,
        ingredients=[
            CocktailIngredientCreate(
                ingredient_id=ingredient.id, amount="2 oz", is_optional=False
            )
        ],
    )
    cocktail = create_cocktail(session, cocktail_in)
    if cocktail.id is None:
        pytest.fail("Cocktail ID was not generated")

    result = delete_cocktail(session, cocktail.id)
    assert result is True

    found = read_cocktail_by_id(session, cocktail.id)
    assert found is None
