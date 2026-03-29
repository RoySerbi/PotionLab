"""Seed script for PotionLab database with real cocktails and ingredients."""

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, create_engine, select

from app.db.session import get_db_url
from app.models import (
    Cocktail,
    CocktailIngredient,
    FlavorTag,
    Ingredient,
    IngredientFlavorTag,
)


def seed_flavor_tags(session: Session) -> int:
    """Seed flavor tags for ingredients."""
    tags_data = [
        {"name": "Citrus", "category": "Fresh"},
        {"name": "Sweet", "category": "Aromatic"},
        {"name": "Bitter", "category": "Complex"},
        {"name": "Herbal", "category": "Aromatic"},
        {"name": "Smoky", "category": "Complex"},
        {"name": "Spicy", "category": "Bold"},
        {"name": "Floral", "category": "Aromatic"},
        {"name": "Fruity", "category": "Fresh"},
        {"name": "Savory", "category": "Complex"},
        {"name": "Earthy", "category": "Complex"},
        {"name": "Fresh", "category": "Fresh"},
        {"name": "Minty", "category": "Fresh"},
    ]

    created = 0
    for tag_data in tags_data:
        try:
            tag = FlavorTag(**tag_data)
            session.add(tag)
            session.commit()
            created += 1
        except IntegrityError:
            session.rollback()

    print(f"✓ Created {created} flavor tags")
    return created


def seed_ingredients(session: Session) -> int:
    """Seed ingredients with flavor tag associations."""
    ingredients_data = [
        # Spirits
        {
            "name": "Gin",
            "category": "Spirit",
            "description": "Juniper-based spirit",
            "flavor_tags": ["Citrus", "Herbal", "Floral"],
        },
        {
            "name": "Vodka",
            "category": "Spirit",
            "description": "Neutral grain spirit",
            "flavor_tags": ["Fresh"],
        },
        {
            "name": "Rum Light",
            "category": "Spirit",
            "description": "Light/white rum",
            "flavor_tags": ["Fruity", "Fresh"],
        },
        {
            "name": "Rum Dark",
            "category": "Spirit",
            "description": "Dark/aged rum",
            "flavor_tags": ["Sweet", "Smoky", "Earthy"],
        },
        {
            "name": "Bourbon",
            "category": "Spirit",
            "description": "American whiskey",
            "flavor_tags": ["Sweet", "Smoky", "Spicy"],
        },
        {
            "name": "Rye Whiskey",
            "category": "Spirit",
            "description": "Rye-based whiskey",
            "flavor_tags": ["Spicy", "Herbal", "Sweet"],
        },
        {
            "name": "Tequila Blanco",
            "category": "Spirit",
            "description": "Clear agave spirit",
            "flavor_tags": ["Citrus", "Fresh", "Herbal"],
        },
        {
            "name": "Mezcal",
            "category": "Spirit",
            "description": "Smoked agave spirit",
            "flavor_tags": ["Smoky", "Earthy", "Spicy"],
        },
        {
            "name": "Brandy",
            "category": "Spirit",
            "description": "Grape-based spirit",
            "flavor_tags": ["Sweet", "Fruity", "Savory"],
        },
        {
            "name": "Cognac",
            "category": "Spirit",
            "description": "Premium brandy",
            "flavor_tags": ["Sweet", "Fruity", "Complex"],
        },
        {
            "name": "Scotch Whisky",
            "category": "Spirit",
            "description": "Scottish whisky",
            "flavor_tags": ["Smoky", "Herbal", "Spicy"],
        },
        # Fortified Wines & Liqueurs
        {
            "name": "Dry Vermouth",
            "category": "Fortified",
            "description": "Dry fortified wine",
            "flavor_tags": ["Herbal", "Bitter"],
        },
        {
            "name": "Sweet Vermouth",
            "category": "Fortified",
            "description": "Sweet fortified wine",
            "flavor_tags": ["Sweet", "Herbal", "Bitter"],
        },
        {
            "name": "Campari",
            "category": "Liqueur",
            "description": "Bitter Italian aperitif",
            "flavor_tags": ["Bitter", "Citrus", "Herbal"],
        },
        {
            "name": "Cointreau",
            "category": "Liqueur",
            "description": "Orange liqueur",
            "flavor_tags": ["Citrus", "Sweet", "Fruity"],
        },
        {
            "name": "Triple Sec",
            "category": "Liqueur",
            "description": "Orange liqueur",
            "flavor_tags": ["Citrus", "Sweet"],
        },
        {
            "name": "Kahlua",
            "category": "Liqueur",
            "description": "Coffee liqueur",
            "flavor_tags": ["Sweet", "Savory"],
        },
        {
            "name": "Creme de Menthe",
            "category": "Liqueur",
            "description": "Mint liqueur",
            "flavor_tags": ["Minty", "Fresh", "Sweet"],
        },
        {
            "name": "Amaretto",
            "category": "Liqueur",
            "description": "Almond liqueur",
            "flavor_tags": ["Sweet", "Fruity"],
        },
        {
            "name": "Chartreuse Green",
            "category": "Liqueur",
            "description": "Herbal liqueur",
            "flavor_tags": ["Herbal", "Floral", "Minty"],
        },
        {
            "name": "Fernet-Branca",
            "category": "Liqueur",
            "description": "Herbal digestif",
            "flavor_tags": ["Herbal", "Bitter", "Minty"],
        },
        # Mixers & Juices
        {
            "name": "Fresh Lime Juice",
            "category": "Juice",
            "description": "Freshly squeezed lime",
            "flavor_tags": ["Citrus", "Fresh"],
        },
        {
            "name": "Fresh Lemon Juice",
            "category": "Juice",
            "description": "Freshly squeezed lemon",
            "flavor_tags": ["Citrus", "Fresh"],
        },
        {
            "name": "Fresh Orange Juice",
            "category": "Juice",
            "description": "Freshly squeezed orange",
            "flavor_tags": ["Citrus", "Fruity", "Fresh"],
        },
        {
            "name": "Ginger Beer",
            "category": "Mixer",
            "description": "Spicy ginger soda",
            "flavor_tags": ["Spicy", "Fresh"],
        },
        {
            "name": "Tonic Water",
            "category": "Mixer",
            "description": "Quinine-flavored mixer",
            "flavor_tags": ["Bitter", "Fresh"],
        },
        {
            "name": "Soda Water",
            "category": "Mixer",
            "description": "Carbonated water",
            "flavor_tags": ["Fresh"],
        },
        {
            "name": "Cola",
            "category": "Mixer",
            "description": "Cola soft drink",
            "flavor_tags": ["Sweet", "Citrus"],
        },
        {
            "name": "Cranberry Juice",
            "category": "Juice",
            "description": "Tart cranberry juice",
            "flavor_tags": ["Citrus", "Fruity", "Sweet"],
        },
        {
            "name": "Simple Syrup",
            "category": "Mixer",
            "description": "Sweetening agent",
            "flavor_tags": ["Sweet"],
        },
        {
            "name": "Espresso",
            "category": "Mixer",
            "description": "Strong coffee",
            "flavor_tags": ["Savory", "Bitter"],
        },
        # Garnishes & Spices
        {
            "name": "Fresh Mint",
            "category": "Garnish",
            "description": "Fresh mint leaves",
            "flavor_tags": ["Minty", "Fresh"],
        },
        {
            "name": "Lime Wheel",
            "category": "Garnish",
            "description": "Lime citrus slice",
            "flavor_tags": ["Citrus", "Fresh"],
        },
        {
            "name": "Lemon Twist",
            "category": "Garnish",
            "description": "Lemon peel twist",
            "flavor_tags": ["Citrus", "Fresh"],
        },
        {
            "name": "Orange Peel",
            "category": "Garnish",
            "description": "Orange citrus peel",
            "flavor_tags": ["Citrus", "Fruity"],
        },
        {
            "name": "Olive",
            "category": "Garnish",
            "description": "Brined olive",
            "flavor_tags": ["Savory", "Bitter"],
        },
        {
            "name": "Cherry",
            "category": "Garnish",
            "description": "Maraschino cherry",
            "flavor_tags": ["Sweet", "Fruity"],
        },
        {
            "name": "Angostura Bitters",
            "category": "Spice",
            "description": "Aromatic bitters",
            "flavor_tags": ["Bitter", "Herbal", "Spicy"],
        },
        {
            "name": "Sugar",
            "category": "Spice",
            "description": "White sugar",
            "flavor_tags": ["Sweet"],
        },
    ]

    created = 0
    for ing_data in ingredients_data:
        flavor_tags = ing_data.pop("flavor_tags")
        try:
            ingredient = Ingredient(**ing_data)
            session.add(ingredient)
            session.commit()
            session.refresh(ingredient)

            # Link flavor tags
            for tag_name in flavor_tags:
                tag = session.exec(
                    select(FlavorTag).where(FlavorTag.name == tag_name)
                ).first()
                if tag:
                    try:
                        link = IngredientFlavorTag(
                            ingredient_id=ingredient.id, flavor_tag_id=tag.id
                        )
                        session.add(link)
                        session.commit()
                    except IntegrityError:
                        session.rollback()

            created += 1
        except IntegrityError:
            session.rollback()

    print(f"✓ Created {created} ingredients with flavor associations")
    return created


def seed_cocktails(session: Session) -> int:
    """Seed real cocktails with accurate recipes."""
    cocktails_data = [
        {
            "name": "Negroni",
            "description": "The quintessential Italian aperitivo",
            "instructions": (
                "Stir gin, Campari, and sweet vermouth with ice. "
                "Strain into a rocks glass over ice. Garnish with orange peel."
            ),
            "glass_type": "Rocks",
            "difficulty": 1,
            "ingredients": [
                ("Gin", "1 oz"),
                ("Campari", "1 oz"),
                ("Sweet Vermouth", "1 oz"),
                ("Orange Peel", "1"),
            ],
        },
        {
            "name": "Martini",
            "description": "The most elegant cocktail in the world",
            "instructions": (
                "Stir gin and dry vermouth with ice. "
                "Strain into a chilled coupe glass. Garnish with olive or lemon twist."
            ),
            "glass_type": "Coupe",
            "difficulty": 2,
            "ingredients": [
                ("Gin", "2.5 oz"),
                ("Dry Vermouth", "0.5 oz"),
                ("Olive", "1"),
            ],
        },
        {
            "name": "Old Fashioned",
            "description": "A classic bourbon cocktail with style",
            "instructions": (
                "Muddle sugar and bitters with a splash of water. "
                "Add bourbon and large ice cube. Stir well. "
                "Garnish with orange peel and cherry."
            ),
            "glass_type": "Rocks",
            "difficulty": 2,
            "ingredients": [
                ("Bourbon", "2 oz"),
                ("Angostura Bitters", "2 dashes"),
                ("Sugar", "1 tsp"),
                ("Orange Peel", "1"),
                ("Cherry", "1"),
            ],
        },
        {
            "name": "Daiquiri",
            "description": "Simple rum, lime, and sugar perfection",
            "instructions": (
                "Shake rum, fresh lime juice, and simple syrup with ice. "
                "Strain into a coupe glass."
            ),
            "glass_type": "Coupe",
            "difficulty": 1,
            "ingredients": [
                ("Rum Light", "2 oz"),
                ("Fresh Lime Juice", "0.75 oz"),
                ("Simple Syrup", "0.5 oz"),
            ],
        },
        {
            "name": "Margarita",
            "description": "The perfect tequila cocktail with citrus",
            "instructions": (
                "Shake tequila, Cointreau, and fresh lime juice with ice. "
                "Strain into a salt-rimmed coupe glass."
            ),
            "glass_type": "Coupe",
            "difficulty": 2,
            "ingredients": [
                ("Tequila Blanco", "2 oz"),
                ("Cointreau", "1 oz"),
                ("Fresh Lime Juice", "0.75 oz"),
                ("Salt", "rim", True),
            ],
        },
        {
            "name": "Mojito",
            "description": "A refreshing rum and mint classic",
            "instructions": (
                "Muddle fresh mint and simple syrup. Add rum and ice. "
                "Top with soda water. Stir well. Garnish with mint sprig."
            ),
            "glass_type": "Highball",
            "difficulty": 3,
            "ingredients": [
                ("Rum Light", "2 oz"),
                ("Fresh Mint", "12 leaves"),
                ("Fresh Lime Juice", "0.75 oz"),
                ("Simple Syrup", "0.75 oz"),
                ("Soda Water", "2 oz"),
            ],
        },
        {
            "name": "Whiskey Sour",
            "description": "Balanced bourbon with citrus and spice",
            "instructions": (
                "Shake bourbon, fresh lemon juice, simple syrup, "
                "and egg white with ice. Strain into rocks glass with ice. "
                "Top with bitters."
            ),
            "glass_type": "Rocks",
            "difficulty": 3,
            "ingredients": [
                ("Bourbon", "2 oz"),
                ("Fresh Lemon Juice", "0.75 oz"),
                ("Simple Syrup", "0.5 oz"),
                ("Angostura Bitters", "2 dashes"),
            ],
        },
        {
            "name": "Cosmopolitan",
            "description": "The modern classic: vodka, cranberry, and citrus",
            "instructions": (
                "Shake vodka, Cointreau, cranberry juice, "
                "and fresh lime juice with ice. Strain into a coupe glass. "
                "Garnish with lime twist."
            ),
            "glass_type": "Coupe",
            "difficulty": 2,
            "ingredients": [
                ("Vodka", "1.5 oz"),
                ("Cointreau", "1 oz"),
                ("Cranberry Juice", "0.75 oz"),
                ("Fresh Lime Juice", "0.5 oz"),
                ("Lime Twist", "1"),
            ],
        },
        {
            "name": "Manhattan",
            "description": "A whiskey classic with vermouth and bitters",
            "instructions": (
                "Stir rye whiskey, sweet vermouth, and bitters with ice. "
                "Strain into a coupe glass. Garnish with cherry."
            ),
            "glass_type": "Coupe",
            "difficulty": 2,
            "ingredients": [
                ("Rye Whiskey", "2 oz"),
                ("Sweet Vermouth", "1 oz"),
                ("Angostura Bitters", "2 dashes"),
                ("Cherry", "1"),
            ],
        },
        {
            "name": "Sazerac",
            "description": "New Orleans legend with rye and absinthe",
            "instructions": (
                "Rinse glass with absinthe. Stir rye, Fernet-Branca, "
                "and bitters with ice. Strain into the rinsed glass. "
                "Garnish with lemon twist."
            ),
            "glass_type": "Rocks",
            "difficulty": 4,
            "ingredients": [
                ("Rye Whiskey", "2 oz"),
                ("Fernet-Branca", "0.5 oz"),
                ("Angostura Bitters", "3 dashes"),
                ("Lemon Twist", "1"),
            ],
        },
        {
            "name": "Espresso Martini",
            "description": "Coffee and vodka for the caffeine lover",
            "instructions": (
                "Shake vodka, Kahlua, and fresh espresso with ice. "
                "Strain into a coupe glass. Garnish with coffee beans."
            ),
            "glass_type": "Coupe",
            "difficulty": 3,
            "ingredients": [
                ("Vodka", "1.5 oz"),
                ("Kahlua", "1 oz"),
                ("Espresso", "1 oz"),
                ("Simple Syrup", "0.5 oz"),
            ],
        },
        {
            "name": "Aperol Spritz",
            "description": "Italian aperitivo with bubbles",
            "instructions": (
                "Build in a wine glass: Aperol, prosecco, and soda water. "
                "Stir gently. Garnish with orange slice."
            ),
            "glass_type": "Wine",
            "difficulty": 1,
            "ingredients": [
                ("Campari", "1.5 oz"),
                ("Soda Water", "3 oz"),
                ("Orange Slice", "1"),
            ],
        },
        {
            "name": "Moscow Mule",
            "description": "Vodka, ginger beer, and lime simplicity",
            "instructions": (
                "Build in a copper mug: vodka and ginger beer. "
                "Stir. Garnish with lime wheel."
            ),
            "glass_type": "Copper Mug",
            "difficulty": 1,
            "ingredients": [
                ("Vodka", "1.5 oz"),
                ("Ginger Beer", "4 oz"),
                ("Fresh Lime Juice", "0.5 oz"),
                ("Lime Wheel", "1"),
            ],
        },
        {
            "name": "Dark & Stormy",
            "description": "Dark rum and spicy ginger beer tradition",
            "instructions": (
                "Build in a rocks glass with ice: dark rum and ginger beer. "
                "Stir well. Garnish with lime wheel."
            ),
            "glass_type": "Rocks",
            "difficulty": 1,
            "ingredients": [
                ("Rum Dark", "2 oz"),
                ("Ginger Beer", "4 oz"),
                ("Lime Wheel", "1"),
            ],
        },
        {
            "name": "Penicillin",
            "description": "Scotch, honey, and ginger warmth",
            "instructions": (
                "Shake Scotch, fresh lemon juice, honey syrup, "
                "and ginger liqueur with ice. Strain into rocks glass with ice. "
                "Garnish with candied ginger."
            ),
            "glass_type": "Rocks",
            "difficulty": 3,
            "ingredients": [
                ("Scotch Whisky", "2 oz"),
                ("Fresh Lemon Juice", "0.75 oz"),
                ("Simple Syrup", "0.75 oz"),
            ],
        },
        {
            "name": "Mai Tai",
            "description": "Tropical rum classic with almond",
            "instructions": (
                "Shake both rums, Cointreau, fresh lime juice, orgeat, "
                "and bitters with ice. Strain into a rocks glass with crushed ice. "
                "Garnish with mint and orange."
            ),
            "glass_type": "Rocks",
            "difficulty": 3,
            "ingredients": [
                ("Rum Light", "1 oz"),
                ("Rum Dark", "1 oz"),
                ("Cointreau", "0.5 oz"),
                ("Fresh Lime Juice", "0.75 oz"),
                ("Amaretto", "0.5 oz"),
                ("Angostura Bitters", "2 dashes"),
                ("Fresh Mint", "sprig"),
                ("Orange Peel", "1"),
            ],
        },
        {
            "name": "Clover Club",
            "description": "Gin, raspberry, and egg white elegance",
            "instructions": (
                "Shake gin, raspberry syrup, fresh lemon juice, "
                "and egg white with ice. Strain into a coupe glass."
            ),
            "glass_type": "Coupe",
            "difficulty": 3,
            "ingredients": [
                ("Gin", "2 oz"),
                ("Fresh Lemon Juice", "0.75 oz"),
                ("Simple Syrup", "0.5 oz"),
            ],
        },
        {
            "name": "Aviation",
            "description": "Gin with floral notes and cherry",
            "instructions": (
                "Shake gin, maraschino liqueur, fresh lemon juice, "
                "and crème de violette with ice. "
                "Strain into a coupe glass."
            ),
            "glass_type": "Coupe",
            "difficulty": 3,
            "ingredients": [
                ("Gin", "2 oz"),
                ("Creme de Menthe", "0.5 oz"),
                ("Fresh Lemon Juice", "0.75 oz"),
            ],
        },
        {
            "name": "Last Word",
            "description": "Equal parts gin, green Chartreuse, and lime",
            "instructions": (
                "Shake gin, green Chartreuse, fresh lime juice, "
                "and maraschino liqueur with ice. "
                "Strain into a coupe glass."
            ),
            "glass_type": "Coupe",
            "difficulty": 3,
            "ingredients": [
                ("Gin", "0.75 oz"),
                ("Chartreuse Green", "0.75 oz"),
                ("Fresh Lime Juice", "0.75 oz"),
                ("Creme de Menthe", "0.75 oz"),
            ],
        },
        {
            "name": "Boulevardier",
            "description": "Whiskey's answer to the Negroni",
            "instructions": (
                "Stir rye whiskey, sweet vermouth, and Campari with ice. "
                "Strain into a coupe glass. Garnish with orange twist."
            ),
            "glass_type": "Coupe",
            "difficulty": 2,
            "ingredients": [
                ("Rye Whiskey", "1.5 oz"),
                ("Sweet Vermouth", "1 oz"),
                ("Campari", "1 oz"),
                ("Orange Twist", "1"),
            ],
        },
        {
            "name": "Sidecar",
            "description": "Brandy, orange, and lemon balance",
            "instructions": (
                "Shake brandy, Cointreau, and fresh lemon juice with ice. "
                "Strain into a coupe glass."
            ),
            "glass_type": "Coupe",
            "difficulty": 2,
            "ingredients": [
                ("Brandy", "1.5 oz"),
                ("Cointreau", "1 oz"),
                ("Fresh Lemon Juice", "0.75 oz"),
            ],
        },
        {
            "name": "Pisco Sour",
            "description": "Peruvian brandy with citrus and spice",
            "instructions": (
                "Shake pisco, fresh lime juice, simple syrup, "
                "egg white, and bitters with ice. Strain into a coupe glass. "
                "Top with bitters."
            ),
            "glass_type": "Coupe",
            "difficulty": 3,
            "ingredients": [
                ("Brandy", "2 oz"),
                ("Fresh Lime Juice", "1 oz"),
                ("Simple Syrup", "0.75 oz"),
                ("Angostura Bitters", "2 dashes"),
            ],
        },
    ]

    created = 0
    for cocktail_data in cocktails_data:
        ingredients_raw = cocktail_data.pop("ingredients")
        try:
            cocktail = Cocktail(**cocktail_data)
            session.add(cocktail)
            session.commit()
            session.refresh(cocktail)

            # Add ingredients to cocktail
            for ing_tuple in ingredients_raw:
                ing_name = ing_tuple[0]
                amount = ing_tuple[1]
                is_optional = ing_tuple[2] if len(ing_tuple) > 2 else False

                ingredient = session.exec(
                    select(Ingredient).where(Ingredient.name == ing_name)
                ).first()

                if ingredient:
                    try:
                        link = CocktailIngredient(
                            cocktail_id=cocktail.id,
                            ingredient_id=ingredient.id,
                            amount=amount,
                            is_optional=is_optional,
                        )
                        session.add(link)
                        session.commit()
                    except IntegrityError:
                        session.rollback()

            created += 1
        except IntegrityError:
            session.rollback()

    print(f"✓ Created {created} cocktails with recipes")
    return created


def main() -> None:
    """Run the seeding process."""
    print("🍹 Seeding PotionLab database...")
    engine = create_engine(get_db_url())

    from app.db.session import init_db

    init_db()

    with Session(engine) as session:
        seed_flavor_tags(session)
        seed_ingredients(session)
        seed_cocktails(session)

    print("✨ Seed complete!")


if __name__ == "__main__":
    main()
