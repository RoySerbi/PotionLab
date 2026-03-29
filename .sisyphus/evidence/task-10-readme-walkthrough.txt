README Verification Walkthrough
===============================

1. uv sync
Resolved 49 packages in 1ms
Checked 44 packages in 0.87ms

2. uv run pytest
................................................                         [100%]
=============================== warnings summary ===============================
tests/test_models.py::test_cocktail_ingredient_composite_pk_prevents_duplicates
  /home/deftera/Documents/Github/lecture-notes/tests/test_models.py:49: SAWarning: New instance <CocktailIngredient at 0x7f41e2bc4440> with identity key (<class 'app.models.cocktail_ingredient.CocktailIngredient'>, (1, 1), None) conflicts with persistent instance <CocktailIngredient at 0x7f41e2bc44d0>
    session.commit()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
48 passed, 1 warning in 0.41s

3. uv run python scripts/seed.py
🍹 Seeding PotionLab database...
✓ Created 0 flavor tags
✓ Created 0 ingredients with flavor associations
✓ Created 0 cocktails with recipes
✨ Seed complete!

4. uv run uvicorn (Check if it starts)
INFO:     Started server process [696588]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [696588]
Uvicorn started and stopped as expected
