# PotionLab — Issues & Gotchas

> Problems encountered and their resolutions.

---

## Task 7

- Attempting to set undeclared attributes (`cocktail.ingredients`) on SQLModel/Pydantic instances raised `ValueError` at runtime.
  - Resolution: Keep service return as SQLModel object and construct nested `CocktailReadFull` in route using explicit helper query data.
- Local LSP diagnostics initially failed because `basedpyright-langserver` was unavailable in PATH.
  - Resolution: install `basedpyright` into project venv and symlink langserver binary into PATH for diagnostics.

## F4 Scope Fidelity (Final Wave)

- Blocking fidelity mismatch: Task 27 acceptance says GET endpoints remain public, but cocktails router currently has app-level auth dependency causing GET auth requirement.
- Spec artifact mismatch: Task 8 requires `data/seed_cocktails.json` + service-layer seeding; current implementation seeds directly in `scripts/seed.py` without JSON source.
- Infrastructure spec mismatch: Task 21 requires multi-stage API Dockerfile; current Dockerfile is single-stage with explicit dev-environment note.
