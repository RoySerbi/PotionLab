import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.clients import PotionLabClient

st.set_page_config(page_title="PotionLab", page_icon="🍹", layout="wide")

api_client = PotionLabClient()


def main() -> None:
    st.title("🍹 PotionLab")
    st.markdown("**Cocktail Recipe Engine & Flavor Chemistry Workbench**")

    page = st.sidebar.radio(
        "Navigation",
        [
            "Cocktail Browser",
            "Ingredient Explorer",
            "Mix a Cocktail",
            "What Can I Make?",
        ],
    )

    if page == "Cocktail Browser":
        show_cocktail_browser()
    elif page == "Ingredient Explorer":
        show_ingredient_explorer()
    elif page == "Mix a Cocktail":
        show_mix_cocktail()
    elif page == "What Can I Make?":
        show_what_can_i_make()


def show_cocktail_browser() -> None:
    st.header("Cocktail Browser")

    cocktails = api_client.list_cocktails()

    if not cocktails:
        st.warning(
            "Unable to connect to PotionLab API. "
            "Please ensure the API server is running on http://localhost:8000"
        )
        return

    st.success(f"Loaded {len(cocktails)} cocktails from API")
    st.info("Cocktail detail view coming soon in Task 13")


def show_ingredient_explorer() -> None:
    st.header("Ingredient Explorer")

    ingredients = api_client.list_ingredients()

    if not ingredients:
        st.warning(
            "Unable to connect to PotionLab API. "
            "Please ensure the API server is running."
        )
        return

    st.success(f"Loaded {len(ingredients)} ingredients from API")
    st.info("Ingredient detail view coming soon in Task 14")


def show_mix_cocktail() -> None:
    st.header("Mix a Cocktail")
    st.info("Cocktail creation form coming soon in Task 15")


def show_what_can_i_make() -> None:
    st.header("What Can I Make?")
    st.info("Ingredient-based cocktail search coming soon in Task 17")


if __name__ == "__main__":
    main()
