# PotionLab — Issues & Gotchas

> Problems encountered and their resolutions.

---

## Task 7

- Attempting to set undeclared attributes (`cocktail.ingredients`) on SQLModel/Pydantic instances raised `ValueError` at runtime.
  - Resolution: Keep service return as SQLModel object and construct nested `CocktailReadFull` in route using explicit helper query data.
- Local LSP diagnostics initially failed because `basedpyright-langserver` was unavailable in PATH.
  - Resolution: install `basedpyright` into project venv and symlink langserver binary into PATH for diagnostics.
