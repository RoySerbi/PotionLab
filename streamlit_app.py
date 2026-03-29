import sys
from pathlib import Path
from typing import Any, cast

import pandas as pd
import plotly.graph_objects as go
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


@st.cache_data(ttl=300)
def fetch_cocktails_with_counts() -> list[dict[str, Any]]:
    cocktails = api_client.list_cocktails()
    result = []
    for c in cocktails:
        detail = api_client.get_cocktail(c["id"])
        c["num_ingredients"] = len(detail.get("ingredients", [])) if detail else 0
        c["flavor_profile"] = detail.get("flavor_profile", []) if detail else []
        result.append(c)
    return result


def difficulty_to_stars(difficulty: int) -> str:
    return "⭐" * difficulty


def render_flavor_tags(tags: list[str]) -> None:
    html = ""
    for tag in tags:
        html += (
            f'<span style="background-color: #E8F5E9; color: #2E7D32; '
            f"padding: 4px 12px; border-radius: 12px; margin: 2px; "
            f'display: inline-block; font-size: 0.9em;">{tag}</span>'
        )
    st.markdown(html, unsafe_allow_html=True)


def render_flavor_radar_chart(tags_dict: dict[str, int], title: str = "") -> None:
    if not tags_dict:
        st.info("No flavor data available for chart.")
        return

    sorted_tags = sorted(tags_dict.items(), key=lambda x: x[1], reverse=True)[:8]
    if not sorted_tags:
        return

    categories = [t[0] for t in sorted_tags]
    values = [t[1] for t in sorted_tags]

    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure(
        data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            fillcolor="rgba(46, 125, 50, 0.4)",
            line=dict(color="#2E7D32", width=2),
            marker=dict(color="#1B5E20", size=6),
            name="Flavor Profile",
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, max(values) if max(values) > 0 else 1]
            ),
            angularaxis=dict(direction="clockwise", period=len(categories) - 1),
        ),
        showlegend=False,
        title=title,
        margin=dict(l=40, r=40, t=40 if title else 20, b=20),
        height=350,
    )

    st.plotly_chart(fig, use_container_width=True)


def show_cocktail_browser() -> None:
    st.header("Cocktail Browser")

    cocktails = fetch_cocktails_with_counts()

    if not cocktails:
        st.warning(
            "Unable to connect to PotionLab API. "
            "Please ensure the API server is running on http://localhost:8000"
        )
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        search_term = st.text_input("Search by name", "")
    with col2:
        difficulty_range = st.slider("Difficulty", 1, 5, (1, 5))
    with col3:
        glass_types = sorted(list({c["glass_type"] for c in cocktails}))
        selected_glasses = st.multiselect("Glass type", glass_types)

    filtered = [
        c
        for c in cocktails
        if (not search_term or search_term.lower() in c["name"].lower())
        and c["difficulty"] >= difficulty_range[0]
        and c["difficulty"] <= difficulty_range[1]
        and (not selected_glasses or c["glass_type"] in selected_glasses)
    ]

    st.success(f"Loaded {len(filtered)} cocktails")

    if not filtered:
        st.info("No cocktails match your filters.")
        return

    from collections import Counter

    all_tags = []
    for c in filtered:
        all_tags.extend(c.get("flavor_profile", []))

    if all_tags:
        st.subheader("Collection Flavor Profile")
        tag_counts = dict(Counter(all_tags))
        render_flavor_radar_chart(tag_counts)

    df = pd.DataFrame(
        [
            {
                "Name": c["name"],
                "Glass Type": c["glass_type"],
                "Difficulty": difficulty_to_stars(c["difficulty"]),
                "# Ingredients": c["num_ingredients"],
            }
            for c in filtered
        ]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Detail View")

    cocktail_names = [c["name"] for c in filtered]
    selected_name = st.selectbox("Select a cocktail to view details:", cocktail_names)

    if selected_name:
        selected_summary = next(
            (c for c in filtered if c["name"] == selected_name), None
        )
        if selected_summary:
            detail = api_client.get_cocktail(selected_summary["id"])
            if detail:
                st.markdown(f"### {detail['name']}")
                st.write(detail.get("description", ""))

                info_col1, info_col2 = st.columns(2)
                with info_col1:
                    st.write(f"**Glass Type:** {detail['glass_type']}")
                with info_col2:
                    st.write(
                        f"**Difficulty:** {difficulty_to_stars(detail['difficulty'])}"
                    )

                if detail.get("flavor_profile"):
                    st.write("**Flavor Profile:**")
                    render_flavor_tags(detail["flavor_profile"])
                    st.write("")

                    cocktail_tags_dict = {tag: 1 for tag in detail["flavor_profile"]}
                    render_flavor_radar_chart(cocktail_tags_dict)

                st.write("**Ingredients:**")
                for ing in detail.get("ingredients", []):
                    opt = " *(Optional)*" if ing.get("is_optional") else ""
                    st.write(f"- {ing['amount']} **{ing['name']}**{opt}")

                with st.expander("Instructions"):
                    st.write(detail.get("instructions", "No instructions provided."))


def show_ingredient_explorer() -> None:
    st.header("Ingredient Explorer")

    ingredients = api_client.list_ingredients()

    if not ingredients:
        st.warning(
            "Unable to connect to PotionLab API. "
            "Please ensure the API server is running."
        )
        return

    categories = sorted({ing.get("category", "Unknown") for ing in ingredients})

    selected_category = st.selectbox("Filter by Category", ["All"] + categories)

    filtered_ingredients = ingredients
    if selected_category != "All":
        filtered_ingredients = [
            ing for ing in ingredients if ing.get("category") == selected_category
        ]

    st.success(f"Showing {len(filtered_ingredients)} of {len(ingredients)} ingredients")

    def get_category_color(cat: str) -> str:
        colors = {
            "Spirit": "#1f77b4",
            "Liqueur": "#ff7f0e",
            "Mixer": "#2ca02c",
            "Juice": "#d62728",
            "Bitters": "#9467bd",
            "Syrup": "#e377c2",
            "Garnish": "#7f7f7f",
        }
        return colors.get(cat, "#17becf")

    cols = st.columns(3)
    for idx, ing in enumerate(filtered_ingredients):
        col = cols[idx % 3]
        with col:
            with st.container(border=True):
                st.markdown(f"### {ing['name']}")

                cat = ing.get("category", "Unknown")
                bg_color = get_category_color(cat)
                st.markdown(
                    f'<span style="background-color:{bg_color}; '
                    f"padding: 2px 8px; border-radius: 12px; "
                    f'font-size: 0.8em; color: white;">{cat}</span>',
                    unsafe_allow_html=True,
                )

                if ing.get("description"):
                    st.caption(ing["description"])

                flavor_tags = ing.get("flavor_tags", [])
                if flavor_tags:
                    tag_html = " ".join(
                        [
                            f'<span style="background-color:#444; '
                            f"padding: 2px 6px; border-radius: 8px; "
                            f"font-size: 0.7em; color: #ddd; "
                            f'margin-right: 4px;">{t.get("name", "")}</span>'
                            for t in flavor_tags
                        ]
                    )
                    st.markdown(tag_html, unsafe_allow_html=True)

    st.divider()
    st.subheader("Find Cocktails by Ingredient")

    cocktails = api_client.list_cocktails()
    if cocktails:
        ing_names = sorted([ing["name"] for ing in ingredients])
        selected_ing_for_cocktails = st.selectbox(
            "Select an ingredient to see which cocktails use it:",
            ["(None)"] + ing_names,
        )

        if selected_ing_for_cocktails != "(None)":
            matching_cocktails = []
            for c in cocktails:
                c_ing_names = [
                    item["ingredient"]["name"]
                    for item in c.get("ingredients", [])
                    if "ingredient" in item
                ]
                if selected_ing_for_cocktails in c_ing_names:
                    matching_cocktails.append(c)

            if matching_cocktails:
                st.write(f"**Cocktails using {selected_ing_for_cocktails}:**")
                for mc in matching_cocktails:
                    st.markdown(f"- **{mc['name']}**: {mc.get('description', '')}")
            else:
                st.info(f"No known cocktails use {selected_ing_for_cocktails}.")


def show_mix_cocktail() -> None:
    st.header("Mix a Cocktail")

    if "mix_form_key" not in st.session_state:
        st.session_state.mix_form_key = 0

    if "ingredients" not in st.session_state:
        st.session_state.ingredients = [
            {"ingredient_id": None, "amount": "", "is_optional": False}
        ]

    if "success_cocktail" in st.session_state:
        cocktail = st.session_state.success_cocktail
        st.success(f"Successfully mixed cocktail: {cocktail['name']}!")
        st.json(cocktail)
        del st.session_state.success_cocktail

    available_ingredients = api_client.list_ingredients()
    ingredient_options = (
        {ing["name"]: ing["id"] for ing in available_ingredients}
        if available_ingredients
        else {}
    )
    ingredient_names = list(ingredient_options.keys())

    glass_types = [
        "coupe",
        "highball",
        "rocks",
        "martini",
        "collins",
        "hurricane",
        "margarita",
        "shot",
    ]

    with st.form(
        f"mix_cocktail_form_{st.session_state.mix_form_key}", clear_on_submit=False
    ):
        st.subheader("1. Basic Information")
        name = st.text_input("Cocktail Name*", max_chars=100)
        description = st.text_area("Description*", max_chars=500)

        col1, col2 = st.columns(2)
        with col1:
            glass_type = st.selectbox("Glass Type", glass_types)
        with col2:
            difficulty = st.slider("Difficulty", min_value=1, max_value=5, value=3)

        st.subheader("2. Ingredients")

        updated_ingredients = []
        action_clicked = None
        action_data = None

        for idx, ing in enumerate(st.session_state.ingredients):
            c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
            with c1:
                default_idx = 0
                if ing["ingredient_id"] in ingredient_options.values():
                    try:
                        ing_name = next(
                            k
                            for k, v in ingredient_options.items()
                            if v == ing["ingredient_id"]
                        )
                        default_idx = ingredient_names.index(ing_name)
                    except (StopIteration, ValueError):
                        pass

                selected_name = st.selectbox(
                    f"Ingredient {idx + 1}*",
                    options=ingredient_names,
                    index=default_idx,
                    key=f"ing_name_{st.session_state.mix_form_key}_{idx}",
                )
                selected_id = ingredient_options.get(selected_name)
            with c2:
                amount = st.text_input(
                    "Amount*",
                    value=ing["amount"],
                    key=f"ing_amt_{st.session_state.mix_form_key}_{idx}",
                    placeholder="e.g., 2 oz",
                )
            with c3:
                is_optional = st.checkbox(
                    "Optional",
                    value=ing["is_optional"],
                    key=f"ing_opt_{st.session_state.mix_form_key}_{idx}",
                )
            with c4:
                st.write("")
                if st.form_submit_button(f"Remove {idx + 1}"):
                    action_clicked = "remove"
                    action_data = idx

            updated_ingredients.append(
                {
                    "ingredient_id": selected_id,
                    "amount": amount,
                    "is_optional": is_optional,
                }
            )

        if st.form_submit_button("➕ Add Ingredient"):
            action_clicked = "add"

        st.subheader("3. Instructions")
        instructions = st.text_area("Mixing Instructions*", height=150)

        submitted = st.form_submit_button("🍸 Mix Cocktail", type="primary")

    if action_clicked == "add":
        st.session_state.ingredients = updated_ingredients
        st.session_state.ingredients.append(
            {"ingredient_id": None, "amount": "", "is_optional": False}
        )
        st.rerun()

    elif action_clicked == "remove" and action_data is not None:
        new_list = [
            item for i, item in enumerate(updated_ingredients) if i != action_data
        ]
        st.session_state.ingredients = new_list
        st.rerun()

    elif submitted:
        errors = []
        if not name.strip():
            errors.append("Cocktail Name is required.")
        if not description.strip():
            errors.append("Description is required.")
        if not instructions.strip():
            errors.append("Instructions are required.")

        valid_ingredients = []
        for i, ing in enumerate(updated_ingredients):
            if not ing["ingredient_id"]:
                errors.append(f"Ingredient {i + 1} must have a valid selection.")
            elif not ing["amount"].strip():
                errors.append(f"Ingredient {i + 1} must have an amount.")
            else:
                valid_ingredients.append(
                    {
                        "ingredient_id": ing["ingredient_id"],
                        "amount": ing["amount"],
                        "is_optional": ing["is_optional"],
                    }
                )

        if not valid_ingredients:
            errors.append("At least one ingredient is required.")

        if errors:
            for error in errors:
                st.error(error)
        else:
            payload = {
                "name": name.strip(),
                "description": description.strip(),
                "instructions": instructions.strip(),
                "glass_type": glass_type,
                "difficulty": difficulty,
                "ingredients": valid_ingredients,
            }

            result = api_client.create_cocktail(payload)
            if result:
                st.session_state.success_cocktail = result
                st.session_state.ingredients = [
                    {"ingredient_id": None, "amount": "", "is_optional": False}
                ]
                st.session_state.mix_form_key += 1
                st.rerun()
            else:
                st.error(
                    "Failed to create cocktail via API. Please check the server logs."
                )


def show_what_can_i_make() -> None:
    st.header("What Can I Make?")

    # Fetch ingredients with caching
    @st.cache_data
    def _get_ingredients() -> list[dict[str, Any]]:
        return cast(list[dict[str, Any]], api_client.list_ingredients())

    ingredients = _get_ingredients()
    ingredient_options = {ing["name"]: ing["id"] for ing in ingredients}

    selected_names = st.multiselect(
        "Select ingredients you have:",
        options=sorted(ingredient_options.keys()),
        help="Choose all the ingredients you currently have available",
    )

    if not selected_names:
        st.info("Select ingredients above to see which cocktails you can make")
        return

    selected_ids = {ingredient_options[name] for name in selected_names}

    # Fetch all cocktails and analyze which can be made
    with st.spinner("Analyzing cocktail possibilities..."):
        all_cocktails = api_client.list_cocktails()
        can_make: list[dict[str, Any]] = []
        almost: list[tuple[dict[str, Any], set[int]]] = []

        # Build ingredient ID to name mapping for display
        ingredient_id_to_name = {ing["id"]: ing["name"] for ing in ingredients}

        for cocktail_summary in all_cocktails:
            cocktail = api_client.get_cocktail(cocktail_summary["id"])
            if not cocktail or "ingredients" not in cocktail:
                continue

            # Get required ingredient IDs (non-optional)
            required_ingredient_ids = {
                ing["ingredient"]["id"]
                for ing in cocktail["ingredients"]
                if not ing.get("is_optional", False)
            }

            missing = required_ingredient_ids - selected_ids

            if len(missing) == 0:
                can_make.append(cocktail)
            elif len(missing) <= 2:
                almost.append((cocktail, missing))

        # Sort almost by number of missing ingredients
        almost.sort(key=lambda x: len(x[1]))

    # Display results
    if can_make:
        st.subheader(f"✅ You Can Make These ({len(can_make)})")
        for cocktail in can_make:
            with st.expander(f"🍸 **{cocktail['name']}**", expanded=False):
                st.markdown(f"*{cocktail.get('description', 'No description')}*")
                st.markdown(f"**Glass:** {cocktail.get('glass_type', 'N/A')}")
                st.markdown(f"**Difficulty:** {cocktail.get('difficulty', 'N/A')}")
                st.markdown("**Ingredients:**")
                for ing in cocktail.get("ingredients", []):
                    ing_name = ing["ingredient"]["name"]
                    amount = ing.get("amount", "")
                    optional = " *(optional)*" if ing.get("is_optional", False) else ""
                    st.markdown(f"- {amount} {ing_name}{optional}")

    if almost:
        st.subheader(f"🔸 Almost There ({len(almost)})")
        st.caption("You're missing 1-2 ingredients for these cocktails")
        for cocktail, missing_ids in almost:
            missing_names = [
                ingredient_id_to_name.get(mid, f"Unknown ({mid})")
                for mid in missing_ids
            ]
            missing_count = len(missing_ids)
            missing_text = ", ".join(missing_names)

            with st.expander(
                f"🥃 **{cocktail['name']}** — Missing {missing_count}: {missing_text}",
                expanded=False,
            ):
                st.markdown(f"*{cocktail.get('description', 'No description')}*")
                st.markdown(f"**Glass:** {cocktail.get('glass_type', 'N/A')}")
                st.markdown(f"**Difficulty:** {cocktail.get('difficulty', 'N/A')}")
                st.markdown(f"**Missing:** {missing_text}")

    if not can_make and not almost:
        st.warning(
            "No cocktails found with your selected ingredients. "
            "Try adding more ingredients!"
        )


if __name__ == "__main__":
    main()
